// RC1-LABS harness: the tool slot of DeviceEvalRunner.answerRow at v2.0.0-rc1 with the six default-on labs.
// The lab wrappers (app/src/labs/plugins/*) are re-written 1:1 here: they only add Android resource loading and Compose UI.
// Order = LabRegistry.active (plugin.properties order, id) stable-sorted by LabTools.slotRank:
//   cohazard(69, rank 0), polyglot(64, rank 1), pulse(10, no answerTool), calc(65), distance(66), facts(67).
// Stub: polyglot's PhoneLanguageDetector (Android TextClassifier) -> null; UI language English.
import java.io.File
import org.json.JSONObject
import team.sopa.boar.engine.rag.Facts
import team.sopa.boar.engine.routing.LabTools
import team.sopa.boar.engine.routing.LanguageGate
import team.sopa.boar.engine.routing.TravelDistance

data class Res(val tool: String, val text: String, val kind: String = "instant")
data class Lab(val id: String, val order: Int, val tool: ((String) -> Res?)?)

fun main(args: Array<String>) {
    val a = args.toList().chunked(2).associate { it[0] to it[1] }
    val facts = Facts(File(a.getValue("--facts")).readText())
    val cities = TravelDistance(File(a.getValue("--cities")).readText())
    val history = emptyList<String>()   // eval rows: AnswerTools.run(q.query, emptyList())
    val polyReply = "Sorry, BOAR doesn't speak {{language}} yet. Ask in English."
    val labs = listOf(
        Lab("pulse", 10, null),
        Lab("polyglot", 64) { q ->
            val d = LanguageGate.decide(q, false) { null }
            (d as? LanguageGate.Decision.Unsupported)?.language?.let { code ->
                Res(LanguageGate.TOOL, polyReply.replace("{{language}}", java.util.Locale.forLanguageTag(code).getDisplayLanguage(java.util.Locale.ENGLISH).ifBlank { code }))
            }
        },
        Lab("calc", 65) { q -> LabTools.calc(q, history)?.let { Res(it.tool, it.text) } },
        Lab("distance", 66) { q -> LabTools.distance(cities, q, history)?.let { Res(it.tool, it.text) } },
        Lab("facts", 67) { q -> LabTools.facts(facts, q, history)?.let { Res(it.tool, it.text) } },
        Lab("cohazard", 69) { q -> LabTools.coHazard(q)?.let { Res(it.tool, it.text) } },
    ).sortedWith(compareBy({ it.order }, { it.id })).sortedBy { LabTools.slotRank(it.id) }
    val slot = labs.mapNotNull { l -> l.tool?.let { l.id to it } }
    System.err.println("slot order: " + slot.joinToString(" > ") { it.first })
    File(a.getValue("--out")).printWriter().use { out ->
        File(a.getValue("--questions")).readLines().filter { it.isNotBlank() }.forEach { line ->
            val q = JSONObject(line)
            val query = q.getString("question")
            // per-lab result (diagnostic) and the slot's first (LabTools.first semantics: a throwing tool is skipped)
            val per = JSONObject()
            slot.forEach { (id, f) -> per.put(id, runCatching { f(query) }.fold({ it?.tool ?: JSONObject.NULL }, { "THROW:" + it.javaClass.simpleName })) }
            val first = LabTools.first(slot) { (id, f) -> f(query)?.let { id to it } }
            out.println(JSONObject().put("id", q.getString("id")).put("lab", first?.first ?: JSONObject.NULL)
                .put("tool", first?.second?.tool ?: JSONObject.NULL).put("kind", first?.second?.kind ?: JSONObject.NULL)
                .put("text", first?.second?.text ?: JSONObject.NULL).put("perLab", per))
        }
    }
}
