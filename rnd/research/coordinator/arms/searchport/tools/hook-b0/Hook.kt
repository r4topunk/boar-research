// SEARCHPORT hook for B0 (engine 078a2627): the plain Retriever, nothing after compression.
import team.sopa.boar.engine.rag.*

object Hook {
    const val NAME = "b0"
    fun retriever(kb: KnowledgeBase, packs: () -> List<OpenPack>, embed: (String) -> FloatArray, lex: () -> Map<String, String>, port: Boolean): Retriever {
        require(!port) { "B0 engine has no port switch" }
        return Retriever(kb, packs, embed, lex)
    }
    fun after(r: Retriever, searchedFor: String, query: String, raw: List<Chunk>, plain: Compress.Result, promptChars: (List<Chunk>) -> Int): Pair<List<Chunk>, List<Chunk>> =
        emptyList<Chunk>() to plain.chunks
    fun preRoute(query: String): String? = null
    fun finalPath(query: String, kept: List<Chunk>): String = "model"
}
