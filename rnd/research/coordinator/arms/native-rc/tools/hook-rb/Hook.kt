// SEARCHPORT Addendum 1/2 hook (rebased branch on lite main): Retriever(port), the per-turn port choice (off / on / nh = on except
// HealthGate.isHealth turns, as AnswerPipeline's plainRetrieve), head pass + SearchPort.fit, QuickMath before the search and the
// HealthGate exposure / fixed-text steps after it (on the final sources), as AnswerPipeline at d92620c0.
import team.sopa.boar.engine.answer.HealthGate
import team.sopa.boar.engine.answer.QuickMath
import team.sopa.boar.engine.rag.*

object Hook {
    const val NAME = "rb"
    fun retriever(kb: KnowledgeBase, packs: () -> List<OpenPack>, embed: (String) -> FloatArray, lex: () -> Map<String, String>, mode: String): Retriever =
        Retriever(kb, packs, embed, lex, port = mode != "off")
    fun portFor(mode: String, query: String, h: ConversationHistory?): Boolean = when (mode) {
        "off" -> false; "on" -> true; "nh" -> !HealthGate.isHealth(query, h); else -> error("mode $mode")
    }
    fun retrieve(r: Retriever, q: String, k: Int, port: Boolean): List<Chunk> = r.retrieve(q, k, port = port)
    fun after(r: Retriever, port: Boolean, searchedFor: String, query: String, raw: List<Chunk>, plain: Compress.Result, promptChars: (List<Chunk>) -> Int): Pair<List<Chunk>, List<Chunk>> {
        val adds = if (port) r.headPass(query, raw, plain.chunks, promptChars) else emptyList()
        return adds to SearchPort.fit(searchedFor, raw, plain, adds).chunks
    }
    fun preRoute(query: String, h: ConversationHistory?): String? = when {
        QuickMath.answer(query, h) != null -> "calc"
        QuickMath.isCalculation(query, h) -> "calc-model"
        else -> null
    }
    fun finalPath(query: String, kept: List<Chunk>, h: ConversationHistory?): String = when {
        HealthGate.exposureAnswer(query, kept) != null -> "exposure"
        HealthGate.fixedText(query, kept, h) != null -> "health-fixed"
        else -> "model"
    }
}
