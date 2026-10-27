// NATIVE-RC PROBES-OFFICIAL harness (harness copy for upstream/main e5c7abe1: conv mode removed; the Boar Labs tool slot added, as
// ChatViewModel at e5c7abe1 runs it before the pipeline: default-on labs cohazard > polyglot > calc > distance > facts, LabTools wrappers re-written
// 1:1 as arms/native-parity/tools/harness-labs did for rc1; polyglot language detector stubbed null). Original header:
// NATIVE-RC harness (copied from native-parity/tools/harness, repointed to wt/judge-clean f1023b93; changes listed in NATIVE-RC.md):
// runs the app's native answer path (AnswerPipeline's plain PIPELINE path, as ChatViewModel runs it with Deep Research off and
// adaptive routing off) up to the prompt, on the desktop JVM, for a questions file. No generation.
// Mode "render" (first arg): the chat's display step after generation (SourceGroups.group + renumber, then
// AnswerText.stripThinking / cleanCitations / splitInlineBullets as ChatScreen shows the answer), from prompts + generations.
// Embeddings: bge-small-en-v1.5 Q8_0 (catalog sha ec38e8da...) through a local llama-server /v1/embeddings.
// Prompt string: the model's own chat template through a llama-server /apply-template (enable_thinking false); tokens through /tokenize.
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.json.*
import team.sopa.boar.engine.answer.AnswerText
import team.sopa.boar.engine.answer.FollowUp
import team.sopa.boar.engine.answer.Personalities
import team.sopa.boar.engine.answer.SourceGroups
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
    @Synchronized fun embed(text: String): FloatArray = cache.getOrPut(text) {
        val r = post("$url/v1/embeddings", buildJsonObject { put("input", text) })
        val v = r.jsonObject["data"]!!.jsonArray[0].jsonObject["embedding"]!!.jsonArray.map { it.jsonPrimitive.float }.toFloatArray()
        cacheFile.appendText(buildJsonObject { put("t", text); put("v", JsonArray(v.map { JsonPrimitive(it) })) }.toString() + "\n")
        v
    }
}

fun arg(args: Array<String>, k: String, d: String? = null): String = args.toList().let { l -> val i = l.indexOf("--$k"); if (i >= 0) l[i + 1] else d ?: error("missing --$k") }

fun cj(c: Chunk) = buildJsonObject {
    put("chunkId", c.chunkId); put("docId", c.docId); put("title", c.title); c.source?.let { put("source", it) }; c.collectionId?.let { put("collectionId", it) }
    put("matchType", c.matchType.name); c.similarity?.let { put("similarity", it) }; c.relevance?.let { put("relevance", it) }; put("score", c.score); put("body", c.body)
}
fun chunkOf(o: JsonObject) = Chunk(o["chunkId"]!!.jsonPrimitive.content, o["docId"]!!.jsonPrimitive.content, o["title"]!!.jsonPrimitive.content,
    o["body"]!!.jsonPrimitive.content, o["source"]?.jsonPrimitive?.content, o["collectionId"]?.jsonPrimitive?.content, o["score"]!!.jsonPrimitive.double,
    MatchType.valueOf(o["matchType"]!!.jsonPrimitive.content), o["similarity"]?.jsonPrimitive?.doubleOrNull, relevance = o["relevance"]?.jsonPrimitive?.doubleOrNull)

/** render <prompts.jsonl> <gen.jsonl> <out.jsonl>: ChatViewModel's grouping + renumber, then ChatScreen's display text. */
fun render(args: Array<String>) {
    val prompts = File(args[1]).readLines().filter { it.isNotBlank() }.map { Json.parseToJsonElement(it).jsonObject }.associateBy { it["arm"]!!.jsonPrimitive.content + "|" + it["id"]!!.jsonPrimitive.content }
    File(args[3]).bufferedWriter().use { w ->
        File(args[2]).forEachLine { l ->
            if (l.isBlank()) return@forEachLine
            val g = Json.parseToJsonElement(l).jsonObject
            val key = g["arm"]!!.jsonPrimitive.content + "|" + g["id"]!!.jsonPrimitive.content
            val p = prompts[key] ?: error("no prompt for $key")
            val kept = p["kept"]!!.jsonArray.map { chunkOf(it.jsonObject) }
            val raw = g["text"]!!.jsonPrimitive.content
            // ChatViewModel: passages -> one per article, best first (similarity ?: relevance), bodies joined with "\n…\n"; the text's [n] renumbered.
            val grouped = SourceGroups.group(kept, { SourceGroups.articleKey(it.source, it.docId, it.title) }, { it.similarity ?: it.relevance }) { gr ->
                gr.first().copy(similarity = gr.mapNotNull { it.similarity }.maxOrNull(), relevance = gr.mapNotNull { it.relevance }.maxOrNull(),
                    body = gr.joinToString("\n…\n") { it.body })
            }
            val stored = SourceGroups.renumber(raw, grouped.renumber)
            // ChatScreen (not streaming): splitInlineBullets(cleanCitations(splitThinking(text).answer, sources.size)).
            val shown = AnswerText.splitInlineBullets(AnswerText.cleanCitations(AnswerText.splitThinking(stored).answer, grouped.items.size))
            val cites = Regex("\\[(\\d{1,4})\\]").findAll(shown).map { it.groupValues[1].toInt() }.filter { it in 1..grouped.items.size }.toSortedSet()
            w.write(buildJsonObject {
                g.forEach { (k, v) -> put(k, v) }
                put("rawText", raw); put("storedText", stored); put("shownText", shown); put("retrievalMs", p["retrievalMs"]!!); put("task", p["task"]!!)
                put("keptN", kept.size); put("promptTokens", p["promptTokens"]!!)
                put("sourcesShown", JsonArray(grouped.items.map(::cj))); put("citedNums", JsonArray(cites.map { JsonPrimitive(it) }))
                put("citationsRaw", Regex("\\[(\\d{1,4})\\]").findAll(raw).count())
            }.toString() + "\n")
        }
    }
}

/** One generation through a llama-server /completion with the native Sampling defaults (tools/s3_gen.py's body). */
fun generate(genUrl: String, prompt: String, nPredict: Int, seed: Int): Triple<String, JsonObject, Double> {
    val t = System.nanoTime()
    val r = post("$genUrl/completion", buildJsonObject {
        put("prompt", prompt); put("n_predict", nPredict); put("temperature", 0.7); put("top_k", 40); put("top_p", 0.95); put("min_p", 0.05)
        put("repeat_penalty", 1.0); put("seed", seed); put("stop", JsonArray(listOf(JsonPrimitive("<|im_end|>")))); put("cache_prompt", false)
    }).jsonObject
    return Triple(r["content"]!!.jsonPrimitive.content.trim(), r, (System.nanoTime() - t) / 1e9)
}

fun main(args: Array<String>) {
    if (args.firstOrNull() == "render") return render(args)
    val questions = File(arg(args, "questions")).readLines().filter { it.isNotBlank() }.map { Json.parseToJsonElement(it).jsonObject }
    val kbPath = arg(args, "kb")
    val corpusDir = File(arg(args, "corpus"))          // snapshot assets/corpus
    // Corpus collections seeded into the KB, as SetupViewModel does: builtin (corpus.json) + the installed corpus assets in catalog order.
    val corpora = arg(args, "corpora", "corpus-standard").split(",").filter { it.isNotBlank() }
    // Packs: "id=path" in the app's order (BoarServices.scanPacks: catalog packs in catalog order with their catalog ids, then local
    // files by name as local-<name>). A question's "packsOff" (list of ids) leaves those packs uninstalled for that question.
    val packSpecs = arg(args, "packs", "").split(",").filter { it.isNotBlank() }.map { s -> s.substringBefore("=") to s.substringAfter("=") }
    val cutoffs = arg(args, "cutoffs", "0.7").split(",").map { it.toDouble() }
    val personas = arg(args, "personas", "succinct").split(",")
    val modelBytes = arg(args, "model-bytes", "1107409472").toLong()   // qwen3-1.7b-q4km (catalog sizeBytes): a "small" model
    val tokUrl = arg(args, "tok")
    val out = File(arg(args, "out"))
    val label = arg(args, "label")
    val emb = Embedder(arg(args, "embed"), File(arg(args, "embed-cache")))
    val personalities = Personalities.parse(File(arg(args, "personalities")).readText())
    val lexicon = Json.parseToJsonElement(File(arg(args, "lexicon")).readText()).jsonObject.mapValues { it.value.jsonPrimitive.content }

    val fresh = !File(kbPath).isFile
    val kb = KnowledgeBase(JdbcSqlite(kbPath))
    if (fresh) runBlocking {
        val cols = listOf(SeedCorpus.Collection(SeedCorpus.BUILTIN, SeedCorpus.docs(SeedCorpus.BUILTIN, File(corpusDir, "corpus.json").readText()))) +
            corpora.map { id -> SeedCorpus.Collection(id, SeedCorpus.docs(id, File(corpusDir, "$id.json").readText())) }
        val n = SeedCorpus(kb) { emb.embed(it) }.seed(cols)
        System.err.println("[harness] seeded $n docs into $kbPath")
    }
    System.err.println("[harness] kb seed chunks ${kb.seedChunkCount()}")
    val allPacks = packSpecs.map { (id, f) ->
        val db = JdbcSqlite(f)
        val meta = db.query("SELECT key, value FROM meta") { it.string(0)!! to (it.string(1) ?: "") }.toMap()
        when (Packs.packFormat(meta, "ec38e8da142596baa913124ae50550de284b6916bf59577ef2f0cb9660c2f514")) {
            1 -> OpenPack.Format1(id, db)
            2 -> OpenPack.Format2(id, WikiPack.open(db, jvmZstd))
            else -> error("not a pack for this embedder: $f")
        }
    }
    System.err.println("[harness] packs " + allPacks.joinToString { "${it.id}:${if (it is OpenPack.Format1) 1 else 2}" })
    var current: List<OpenPack> = allPacks
    val retriever = Retriever(kb, { current }, emb::embed, { lexicon })
    val small = modelBytes < Personalities.SMALL_MODEL_BYTES
    // Boar Labs tool slot (--labs on): order = LabRegistry.active by plugin order, stable-sorted by LabTools.slotRank.
    val labSlot: ((String) -> Triple<String, String, String>?)? = if (arg(args, "labs", "off") != "on") null else {
        val facts = team.sopa.boar.engine.rag.Facts(File(arg(args, "facts")).readText())
        val cities = team.sopa.boar.engine.routing.TravelDistance(File(arg(args, "cities")).readText())
        val hist = emptyList<String>()
        val polyReply = "Sorry, BOAR doesn't speak {{language}} yet. Ask in English."
        val labs: List<Pair<String, (String) -> Pair<String, String>?>> = listOf(
            "cohazard" to { q: String -> team.sopa.boar.engine.routing.LabTools.coHazard(q)?.let { it.tool to it.text } },
            "polyglot" to { q: String -> (team.sopa.boar.engine.routing.LanguageGate.decide(q, false) { null } as? team.sopa.boar.engine.routing.LanguageGate.Decision.Unsupported)?.language?.let { code ->
                team.sopa.boar.engine.routing.LanguageGate.TOOL to polyReply.replace("{{language}}", java.util.Locale.forLanguageTag(code).getDisplayLanguage(java.util.Locale.ENGLISH).ifBlank { code }) } },
            "calc" to { q: String -> team.sopa.boar.engine.routing.LabTools.calc(q, hist)?.let { it.tool to it.text } },
            "distance" to { q: String -> team.sopa.boar.engine.routing.LabTools.distance(cities, q, hist)?.let { it.tool to it.text } },
            "facts" to { q: String -> team.sopa.boar.engine.routing.LabTools.facts(facts, q, hist)?.let { it.tool to it.text } },
        );
        { q: String -> team.sopa.boar.engine.routing.LabTools.first(labs) { (id, f) -> f(q)?.let { Triple(id, it.first, it.second) } } }
    }

    out.parentFile.mkdirs()
    out.bufferedWriter().use { w ->
        for (cut in cutoffs) {
            System.setProperty("boar.cutoff", cut.toString())
            for (q in questions) {
                val id = q["id"]!!.jsonPrimitive.content
                val arm = q["arm"]?.jsonPrimitive?.content ?: label
                val query = q["question"]!!.jsonPrimitive.content
                val off = q["packsOff"]?.jsonArray?.map { it.jsonPrimitive.content }?.toSet() ?: emptySet()
                val unknown = off - allPacks.map { it.id }.toSet()
                if (unknown.isNotEmpty()) error("$id: packsOff not in kit: $unknown")
                current = allPacks.filter { it.id !in off }
                val hit = labSlot?.invoke(query)
                if (hit != null) {
                    // ToolResult.Instant: the chat shows the tool's text, no retrieval, no model (ChatViewModel e5c7abe1).
                    w.write(buildJsonObject { put("label", label); put("arm", arm); put("id", id); put("question", query); put("instant", true)
                        put("lab", hit.first); put("tool", hit.second); put("text", hit.third); put("persona", personas[0]) }.toString() + "\n"); w.flush(); continue
                }
                val task = Classify.classifyTask(query).value
                val retrieved = !Classify.isRetrievalIrrelevant(TaskType.of(task))
                var raw: List<Chunk> = emptyList(); var kept: List<Chunk> = emptyList(); var before: Int? = null; var after: Int? = null
                val t0 = System.nanoTime()
                if (retrieved) {
                    // AnswerPipeline: FollowUp.search(query, history = null for a first turn) over retrieve(it, ANSWER_CONTEXT_CHUNKS = 4), then Compress.forAnswer.
                    val found = FollowUp.search(query, null, { c: Chunk -> "${c.title} ${c.body}" }) { retriever.retrieve(it, 4) }
                    raw = found.chunks
                    val c = Compress.forAnswer(found.searchedFor, found.chunks, task)
                    kept = c.chunks; before = c.tokensBefore; after = c.tokensAfter
                }
                val retrMs = (System.nanoTime() - t0) / 1e6
                for (persona in personas) {
                    // ChatViewModel: style = succinct (AppSettings.personalityId is always ANSWER_STYLE); ShortAnswer only moves Detailed.
                    val style = if (persona == "detailed" && ShortAnswer.reason("detailed", query, null) != null) "succinct" else persona
                    val (sys, reminder) = personalities.promptFor(style, null, small)
                    // AppSettings.answerTokens(openedContext): Succinct Auto 512 fitted to n_ctx (4096 on >= 6.5 GB phones: 512); small talk min(.., 512).
                    val auto = AppSettings.fitToContext(AppSettings.autoMaxTokens(persona), arg(args, "ctx", "4096").toInt())
                    val maxTokens = if (ShortAnswer.isSmallTalk(query)) minOf(auto, AppSettings.AUTO_MAX_TOKENS) else auto
                    val msgs = RagPure.assembleChatMessages(query, kept, sys, null, reminder)
                    val tpl = post("$tokUrl/apply-template", buildJsonObject {
                        put("messages", JsonArray(msgs.map { m -> buildJsonObject { put("role", m.role); put("content", m.content) } }))
                    }).jsonObject["prompt"]!!.jsonPrimitive.content
                    val ntok = post("$tokUrl/tokenize", buildJsonObject { put("content", tpl); put("add_special", false); put("parse_special", true) })
                        .jsonObject["tokens"]!!.jsonArray.size
                    w.write(buildJsonObject {
                        put("label", label); put("arm", arm); put("id", id); put("question", query); put("cutoff", cut); put("persona", persona); put("style", style)
                        put("packsOff", JsonArray(off.sorted().map { JsonPrimitive(it) })); put("packsOn", JsonArray(current.map { JsonPrimitive(it.id) }))
                        put("small", small); put("task", task); put("retrieveRan", retrieved); put("retrievalUsed", kept.isNotEmpty())
                        put("messages", JsonArray(msgs.map { m -> buildJsonObject { put("role", m.role); put("content", m.content) } }))
                        put("raw", JsonArray(raw.map(::cj))); put("kept", JsonArray(kept.map(::cj)))
                        before?.let { put("tokensBefore", it) }; after?.let { put("tokensAfter", it) }
                        put("retrievalMs", retrMs); put("maxTokens", maxTokens); put("promptTokens", ntok); put("prompt", tpl)
                    }.toString() + "\n")
                    w.flush()
                }
            }
            System.err.println("[harness] $label cutoff $cut done")
        }
    }
}
