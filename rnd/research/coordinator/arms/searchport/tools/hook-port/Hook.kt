// SEARCHPORT hook for the port branch (boarlite/search-port): Retriever(port), its head pass after compression, and (from the
// P1b fix on) SearchPort.fit, exactly as AnswerPipeline runs them. Returns the final passages (kept list) for the question.
import team.sopa.boar.engine.rag.*

object Hook {
    const val NAME = "port"
    fun retriever(kb: KnowledgeBase, packs: () -> List<OpenPack>, embed: (String) -> FloatArray, lex: () -> Map<String, String>, port: Boolean): Retriever =
        Retriever(kb, packs, embed, lex, port = port)
    /** (appends picked, final passages) after compression of [raw] into [plain]. */
    fun after(r: Retriever, searchedFor: String, query: String, raw: List<Chunk>, plain: Compress.Result, promptChars: (List<Chunk>) -> Int): Pair<List<Chunk>, List<Chunk>> {
        val adds = r.headPass(query, raw, plain.chunks, promptChars)
        return adds to SearchPort.fit(searchedFor, raw, plain, adds).chunks
    }
    fun preRoute(query: String): String? = null
    fun finalPath(query: String, kept: List<Chunk>): String = "model"
}
