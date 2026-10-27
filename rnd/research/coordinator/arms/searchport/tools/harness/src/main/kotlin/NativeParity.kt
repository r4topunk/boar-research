// SEARCHPORT harness (arms/searchport: retriever + post-compression append through Hook; keptFull/wallMs rows for the retbench scorer;
// --tok none skips the prompt string). Originally: NATIVE-RC harness (copied from native-parity/tools/harness, repointed to wt/judge-clean f1023b93; changes listed in NATIVE-RC.md):
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

/**
 * conv: whole conversations through ChatViewModel's PIPELINE path, turn by turn, generating inline (--gen = a llama-server /completion URL).
 * History as ChatViewModel builds it: prior messages with text (user question, assistant text as saved = renumbered), last VERBATIM_MESSAGE_COUNT (6),
 * assistant text through stripThinking, HistoryBudget.budget; summary null (the app writes one only past historyTurnThreshold turns). Never logs item text.
 */
fun conv(args: Array<String>) {
    val items = File(arg(args, "items")).readLines().filter { it.isNotBlank() }.map { Json.parseToJsonElement(it).jsonObject }
    val genUrl = arg(args, "gen"); val seed = arg(args, "seed").toInt(); val tokUrl = arg(args, "tok"); val out = File(arg(args, "out"))
    val emb = Embedder(arg(args, "embed"), File(arg(args, "embed-cache")))
    val personalities = Personalities.parse(File(arg(args, "personalities")).readText())
    val lexicon = Json.parseToJsonElement(File(arg(args, "lexicon")).readText()).jsonObject.mapValues { it.value.jsonPrimitive.content }
    val kb = KnowledgeBase(JdbcSqlite(arg(args, "kb").also { require(File(it).isFile) { "seed the KB first (prompts mode)" } }))
    val packs = arg(args, "packs", "").split(",").filter { it.isNotBlank() }.map { s -> s.substringBefore("=") to s.substringAfter("=") }.map { (id, f) ->
        val db = JdbcSqlite(f)
        val meta = db.query("SELECT key, value FROM meta") { it.string(0)!! to (it.string(1) ?: "") }.toMap()
        when (Packs.packFormat(meta, "ec38e8da142596baa913124ae50550de284b6916bf59577ef2f0cb9660c2f514")) {
            1 -> OpenPack.Format1(id, db); 2 -> OpenPack.Format2(id, WikiPack.open(db, jvmZstd)); else -> error("not a pack: $f")
        }
    }
    val retriever = Retriever(kb, { packs }, emb::embed, { lexicon })
    val small = arg(args, "model-bytes", "1107409472").toLong() < Personalities.SMALL_MODEL_BYTES
    val (sys, reminder) = personalities.promptFor("succinct", null, small)
    val done = if (out.isFile) out.readLines().filter { it.isNotBlank() }.map { Json.parseToJsonElement(it).jsonObject["id"]!!.jsonPrimitive.content }.toSet() else emptySet()
    var recapTurns = 0
    out.parentFile.mkdirs()
    java.io.FileWriter(out, true).buffered().use { w ->
        for (item in items) {
            val id = item["id"]!!.jsonPrimitive.content
            if (id in done) continue
            val turns = item["turns"]!!.jsonArray.map { it.jsonPrimitive.content }
            val prior = ArrayList<ConversationTurn>()           // messages with text, as saved
            val exchanges = ArrayList<team.sopa.boar.engine.answer.DeepResearch.Companion.Exchange>()
            val rows = ArrayList<JsonObject>()
            for ((k, q) in turns.withIndex()) {
                val history = ConversationHistory(summary = null, turns = team.sopa.boar.engine.answer.HistoryBudget.budget(prior.takeLast(6).map {
                    ConversationTurn(it.role, if (it.role == "assistant") AnswerText.stripThinking(it.text) else it.text) }))
                // ChatViewModel.aboutConversation: such a turn takes the RECAP path (Deep Research write-up); recorded, answered here by the pipeline.
                val recap = (team.sopa.boar.engine.answer.DeepResearch.isConversationRecap(q) && exchanges.any { !team.sopa.boar.engine.answer.DeepResearch.isConversationRecap(it.question) && !team.sopa.boar.engine.answer.DeepResearch.isSummaryFollowUp(it.question) }) ||
                    (team.sopa.boar.engine.answer.DeepResearch.isSummaryFollowUp(q) && team.sopa.boar.engine.answer.DeepResearch.lastAnswered(q, history) != null)
                if (recap) recapTurns++
                val task = Classify.classifyTask(q).value
                val retrieved = !Classify.isRetrievalIrrelevant(TaskType.of(task))
                var kept: List<Chunk> = emptyList()
                val t0 = System.nanoTime()
                if (retrieved) {
                    val found = FollowUp.search(q, history, { c: Chunk -> "${c.title} ${c.body}" }) { retriever.retrieve(it, 4) }
                    kept = Compress.forAnswer(found.searchedFor, found.chunks, task).chunks
                }
                val retrMs = (System.nanoTime() - t0) / 1e6
                val auto = AppSettings.fitToContext(AppSettings.autoMaxTokens("succinct"), arg(args, "ctx", "4096").toInt())
                val maxTokens = if (ShortAnswer.isSmallTalk(q)) minOf(auto, AppSettings.AUTO_MAX_TOKENS) else auto
                val msgs = RagPure.assembleChatMessages(q, kept, sys, history, reminder)
                val tpl = post("$tokUrl/apply-template", buildJsonObject {
                    put("messages", JsonArray(msgs.map { m -> buildJsonObject { put("role", m.role); put("content", m.content) } }))
                }).jsonObject["prompt"]!!.jsonPrimitive.content
                val (raw, resp, wall) = generate(genUrl, tpl, maxTokens, seed)
                val grouped = SourceGroups.group(kept, { SourceGroups.articleKey(it.source, it.docId, it.title) }, { it.similarity ?: it.relevance }) { gr ->
                    gr.first().copy(similarity = gr.mapNotNull { it.similarity }.maxOrNull(), relevance = gr.mapNotNull { it.relevance }.maxOrNull(), body = gr.joinToString("\n…\n") { it.body })
                }
                val stored = SourceGroups.renumber(raw, grouped.renumber)
                val shown = AnswerText.splitInlineBullets(AnswerText.cleanCitations(AnswerText.splitThinking(stored).answer, grouped.items.size))
                prior += ConversationTurn("user", q); if (stored.isNotEmpty()) prior += ConversationTurn("assistant", stored)
                if (stored.isNotBlank()) exchanges += team.sopa.boar.engine.answer.DeepResearch.Companion.Exchange(q, AnswerText.stripThinking(stored))
                rows += buildJsonObject {
                    put("turn", k + 1); put("task", task); put("recapRoute", recap); put("historyTurns", history.turns.size); put("keptN", kept.size)
                    put("kept", JsonArray(kept.map(::cj))); put("sourcesShownTitles", JsonArray(grouped.items.map { JsonPrimitive(it.title) }))
                    put("rawText", raw); put("storedText", stored); put("shownText", shown); put("maxTokens", maxTokens)
                    put("tokens_predicted", resp["tokens_predicted"] ?: JsonNull); put("tokens_evaluated", resp["tokens_evaluated"] ?: JsonNull)
                    put("stopped_limit", (resp["stop_type"]?.jsonPrimitive?.contentOrNull == "limit") || (resp["stopped_limit"]?.jsonPrimitive?.booleanOrNull == true))
                    put("wall_s", wall); put("retrievalMs", retrMs)
                }
            }
            val answer = if (rows.size == 1) rows[0]["shownText"]!!.jsonPrimitive.content
            else rows.joinToString("\n\n") { "[Turn ${it["turn"]}]\n${it["shownText"]!!.jsonPrimitive.content}" }
            w.write(buildJsonObject { put("id", id); put("seed", seed); put("nTurns", rows.size); put("answer", answer); put("turns", JsonArray(rows)) }.toString() + "\n"); w.flush()
            System.err.println("[conv] $id turns ${rows.size}")
        }
    }
    System.err.println("[conv] done, recap-routed turns $recapTurns")
}

fun main(args: Array<String>) {
    if (args.firstOrNull() == "render") return render(args)
    if (args.firstOrNull() == "conv") return conv(args)
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
    val mode = arg(args, "port", "off")
    val port = mode != "off"
    val retriever = Hook.retriever(kb, { current }, emb::embed, { lexicon }, mode)
    System.err.println("[harness] hook ${Hook.NAME} port $port")
    val small = modelBytes < Personalities.SMALL_MODEL_BYTES
    val (sysS, remS) = personalities.promptFor("succinct", null, small)
    val promptChars = { q: String, h: ConversationHistory?, s: List<Chunk> -> RagPure.assembleChatMessages(q, s, sysS, h, remS).sumOf { it.role.length + it.content.length } }

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
                val task = Classify.classifyTask(query).value
                val hist = q["history"]?.jsonObject?.get("turns")?.jsonArray?.map { t -> ConversationTurn(t.jsonObject["role"]!!.jsonPrimitive.content, t.jsonObject["text"]!!.jsonPrimitive.content) }
                    ?.let { ConversationHistory(null, it) }
                val pre = Hook.preRoute(query, hist)
                val portTurn = Hook.portFor(mode, query, hist)
                val retrieved = !Classify.isRetrievalIrrelevant(TaskType.of(task)) && pre == null
                var raw: List<Chunk> = emptyList(); var kept: List<Chunk> = emptyList(); var appended: List<Chunk> = emptyList(); var before: Int? = null; var after: Int? = null
                val t0 = System.nanoTime()
                if (retrieved) {
                    // AnswerPipeline: FollowUp.search(query, history = null for a first turn) over retrieve(it, ANSWER_CONTEXT_CHUNKS = 4), then Compress.forAnswer.
                    val found = FollowUp.search(query, hist, { c: Chunk -> "${c.title} ${c.body}" }) { Hook.retrieve(retriever, it, 4, portTurn) }
                    raw = found.chunks
                    val c = Compress.forAnswer(found.searchedFor, found.chunks, task)
                    before = c.tokensBefore; after = c.tokensAfter
                    val (adds, fin) = Hook.after(retriever, portTurn, found.searchedFor, query, raw, c) { promptChars(query, hist, it) }
                    appended = adds; kept = fin
                }
                val retrMs = (System.nanoTime() - t0) / 1e6
                val path = if (pre == "calc") "calc" else Hook.finalPath(query, kept, hist)
                for (persona in personas) {
                    // ChatViewModel: style = succinct (AppSettings.personalityId is always ANSWER_STYLE); ShortAnswer only moves Detailed.
                    val style = if (persona == "detailed" && ShortAnswer.reason("detailed", query, null) != null) "succinct" else persona
                    val (sys, reminder) = personalities.promptFor(style, null, small)
                    // AppSettings.answerTokens(openedContext): Succinct Auto 512 fitted to n_ctx (4096 on >= 6.5 GB phones: 512); small talk min(.., 512).
                    val auto = AppSettings.fitToContext(AppSettings.autoMaxTokens(persona), arg(args, "ctx", "4096").toInt())
                    val maxTokens = if (ShortAnswer.isSmallTalk(query)) minOf(auto, AppSettings.AUTO_MAX_TOKENS) else auto
                    val msgs = RagPure.assembleChatMessages(query, kept, sys, hist, reminder)
                    val tpl = if (tokUrl == "none") "" else post("$tokUrl/apply-template", buildJsonObject {
                        put("messages", JsonArray(msgs.map { m -> buildJsonObject { put("role", m.role); put("content", m.content) } }))
                    }).jsonObject["prompt"]!!.jsonPrimitive.content
                    val ntok = if (tokUrl == "none") -1 else post("$tokUrl/tokenize", buildJsonObject { put("content", tpl); put("add_special", false); put("parse_special", true) })
                        .jsonObject["tokens"]!!.jsonArray.size
                    w.write(buildJsonObject {
                        put("label", label); put("arm", arm); put("id", id); put("question", query); put("cutoff", cut); put("persona", persona); put("style", style)
                        put("packsOff", JsonArray(off.sorted().map { JsonPrimitive(it) })); put("packsOn", JsonArray(current.map { JsonPrimitive(it.id) }))
                        put("small", small); put("task", task); put("retrieveRan", retrieved); put("retrievalUsed", kept.isNotEmpty())
                        put("messages", JsonArray(msgs.map { m -> buildJsonObject { put("role", m.role); put("content", m.content) } }))
                        put("raw", JsonArray(raw.map(::cj))); put("kept", JsonArray(kept.map(::cj))); put("keptFull", JsonArray(kept.map(::cj)))
                        put("appended", JsonArray(appended.map { JsonPrimitive(it.chunkId) })); put("appendedKept", JsonArray(appended.filter { a -> kept.any { it.chunkId == a.chunkId } }.map { JsonPrimitive(it.chunkId) })); put("wallMs", retrMs); put("path", path); put("portTurn", portTurn); put("hook", Hook.NAME); put("port", port)
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
