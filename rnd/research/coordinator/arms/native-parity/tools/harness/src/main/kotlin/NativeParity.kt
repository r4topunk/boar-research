// NATIVE-PARITY harness: runs the maintainer's native answer path (AnswerPipeline's fixed-model path, as the app's chat
// and DeviceEvalRunner run it) up to the prompt, on the desktop JVM, for a questions file. No generation.
// Embeddings: bge-small-en-v1.5 Q8_0 (the catalog's sha ec38e8da...) through a local llama-server /v1/embeddings.
// Prompt string: the model's own chat template through a llama-server /apply-template; tokens through /tokenize.
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.json.*
import team.sopa.boar.engine.answer.FollowUp
import team.sopa.boar.engine.answer.Personalities
import team.sopa.boar.engine.db.JdbcSqlite
import team.sopa.boar.engine.db.jvmZstd
import team.sopa.boar.engine.rag.*
import team.sopa.boar.engine.routing.Classify
import team.sopa.boar.engine.routing.ShortAnswer
import team.sopa.boar.engine.routing.TaskType
import team.sopa.boar.engine.settings.AppSettings
import java.io.File
import java.net.URI
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse

val http: HttpClient = HttpClient.newHttpClient()
fun post(url: String, body: JsonElement): JsonElement {
    val r = http.send(HttpRequest.newBuilder(URI(url)).header("Content-Type", "application/json")
        .POST(HttpRequest.BodyPublishers.ofString(body.toString())).build(), HttpResponse.BodyHandlers.ofString())
    if (r.statusCode() != 200) error("HTTP ${r.statusCode()} $url: ${r.body().take(300)}")
    return Json.parseToJsonElement(r.body())
}

class Embedder(private val url: String, private val cacheFile: File) {
    private val cache = HashMap<String, FloatArray>()
    init {
        if (cacheFile.isFile) cacheFile.forEachLine { l ->
            val o = Json.parseToJsonElement(l).jsonObject
            cache[o["t"]!!.jsonPrimitive.content] = o["v"]!!.jsonArray.map { it.jsonPrimitive.float }.toFloatArray()
        }
    }
    fun embed(text: String): FloatArray = cache.getOrPut(text) {
        val r = post("$url/v1/embeddings", buildJsonObject { put("input", text) })
        val v = r.jsonObject["data"]!!.jsonArray[0].jsonObject["embedding"]!!.jsonArray.map { it.jsonPrimitive.float }.toFloatArray()
        cacheFile.appendText(buildJsonObject { put("t", text); put("v", JsonArray(v.map { JsonPrimitive(it) })) }.toString() + "\n")
        v
    }
}

fun arg(args: Array<String>, k: String, d: String? = null): String = args.toList().let { l -> val i = l.indexOf("--$k"); if (i >= 0) l[i + 1] else d ?: error("missing --$k") }

fun main(args: Array<String>) {
    val questions = File(arg(args, "questions")).readLines().filter { it.isNotBlank() }.map { Json.parseToJsonElement(it).jsonObject }
    val kbPath = arg(args, "kb")
    val corpusDir = File(arg(args, "corpus"))          // wt/native-qa/assets/corpus (corpus.json + corpus-standard.json)
    val packFiles = arg(args, "packs", "").split(",").filter { it.isNotBlank() }
    val cutoffs = arg(args, "cutoffs", "0.7").split(",").map { it.toDouble() }
    val personas = arg(args, "personas", "detailed,succinct").split(",")
    val modelBytes = arg(args, "model-bytes", "986048768").toLong()   // qwen2.5-1.5b-instruct-q4km (catalog sizeBytes): a "small" model
    val tokUrl = arg(args, "tok")
    val out = File(arg(args, "out"))
    val label = arg(args, "label")
    val emb = Embedder(arg(args, "embed"), File(arg(args, "embed-cache")))
    val personalities = Personalities.parse(File(arg(args, "personalities")).readText())
    val lexicon = Json.parseToJsonElement(File(arg(args, "lexicon")).readText()).jsonObject.mapValues { it.value.jsonPrimitive.content }

    // Knowledge base: the Standard tier = bundled corpus.json ("builtin") + corpus-standard.json, seeded as SetupViewModel does.
    val fresh = !File(kbPath).isFile
    val kb = KnowledgeBase(JdbcSqlite(kbPath))
    if (fresh) runBlocking {
        val cols = listOf(
            SeedCorpus.Collection(SeedCorpus.BUILTIN, SeedCorpus.docs(SeedCorpus.BUILTIN, File(corpusDir, "corpus.json").readText())),
            SeedCorpus.Collection("corpus-standard", SeedCorpus.docs("corpus-standard", File(corpusDir, "corpus-standard.json").readText())),
        )
        val n = SeedCorpus(kb) { emb.embed(it) }.seed(cols)
        System.err.println("[harness] seeded $n docs into $kbPath")
    }
    System.err.println("[harness] kb seed chunks ${kb.seedChunkCount()}")
    // Local pack files in name order, ids local-<name> (DeviceEvalRunner.openRetrieval).
    val packs = packFiles.sortedBy { File(it).name }.map { f ->
        val db = JdbcSqlite(f)
        val meta = db.query("SELECT key, value FROM meta") { it.string(0)!! to (it.string(1) ?: "") }.toMap()
        val id = "local-${File(f).name.removeSuffix(".sqlite")}"
        when (Packs.packFormat(meta, "ec38e8da142596baa913124ae50550de284b6916bf59577ef2f0cb9660c2f514")) {
            1 -> OpenPack.Format1(id, db)
            2 -> OpenPack.Format2(id, WikiPack.open(db, jvmZstd))
            else -> error("not a pack for this embedder: $f")
        }
    }
    val retriever = Retriever(kb, { packs }, emb::embed, { lexicon })
    val small = modelBytes < Personalities.SMALL_MODEL_BYTES

    out.parentFile.mkdirs()
    out.bufferedWriter().use { w ->
        for (cut in cutoffs) {
            System.setProperty("boar.cutoff", cut.toString())
            for (q in questions) {
                val id = q["id"]!!.jsonPrimitive.content
                val query = q["question"]!!.jsonPrimitive.content
                val task = Classify.classifyTask(query).value
                val retrieved = !Classify.isRetrievalIrrelevant(TaskType.of(task))
                var raw: List<Chunk> = emptyList(); var kept: List<Chunk> = emptyList(); var before: Int? = null; var after: Int? = null
                val t0 = System.nanoTime()
                if (retrieved) {
                    val found = FollowUp.search(query, null, { c: Chunk -> "${c.title} ${c.body}" }) { retriever.retrieve(it, 4) }
                    raw = found.chunks
                    val c = Compress.forAnswer(found.searchedFor, found.chunks, task)
                    kept = c.chunks; before = c.tokensBefore; after = c.tokensAfter
                }
                val retrMs = (System.nanoTime() - t0) / 1e6
                for (persona in personas) {
                    // DeviceEvalRunner: Detailed falls back to Succinct for small talk / health / seed questions (ShortAnswer).
                    val style = if (persona == "detailed" && ShortAnswer.reason("detailed", query, null) != null) "succinct" else persona
                    val (sys, reminder) = personalities.promptFor(style, null, small)
                    val auto = AppSettings.autoMaxTokens(persona)
                    val maxTokens = if (ShortAnswer.isSmallTalk(query)) minOf(auto, AppSettings.AUTO_MAX_TOKENS) else auto
                    val msgs = RagPure.assembleChatMessages(query, kept, sys, null, reminder)
                    val tpl = post("$tokUrl/apply-template", buildJsonObject {
                        put("messages", JsonArray(msgs.map { m -> buildJsonObject { put("role", m.role); put("content", m.content) } }))
                    }).jsonObject["prompt"]!!.jsonPrimitive.content
                    val ntok = post("$tokUrl/tokenize", buildJsonObject { put("content", tpl); put("add_special", false); put("parse_special", true) })
                        .jsonObject["tokens"]!!.jsonArray.size
                    fun cj(c: Chunk) = buildJsonObject {
                        put("chunkId", c.chunkId); put("title", c.title); put("source", c.source); put("matchType", c.matchType.name)
                        c.similarity?.let { put("similarity", it) }; put("score", c.score); put("body", c.body)
                    }
                    w.write(buildJsonObject {
                        put("label", label); put("id", id); put("question", query); put("cutoff", cut); put("persona", persona); put("style", style)
                        put("small", small); put("task", task); put("retrieveRan", retrieved); put("retrievalUsed", kept.isNotEmpty())
                        put("raw", JsonArray(raw.map(::cj))); put("kept", JsonArray(kept.map(::cj)))
                        before?.let { put("tokensBefore", it) }; after?.let { put("tokensAfter", it) }
                        put("retrievalMs", retrMs); put("maxTokens", maxTokens); put("promptTokens", ntok); put("prompt", tpl)
                    }.toString() + "\n")
                }
            }
            System.err.println("[harness] $label cutoff $cut done")
        }
    }
}
