"""HONESTPROMPT prompt assembly = RagPure.assemblePrompt (UPSTREAM_REPO/boar-app upstream/fullnative-dev, android-native/engine/.../rag/RagPure.kt), read-only via git show.
The Kotlin being ported (verbatim):

    private fun instructionOf(systemPrompt: String?) =
        if (systemPrompt != null && systemPrompt.trim().isNotEmpty()) systemPrompt.trim() else "You are an offline research assistant."
    private fun styleSection(styleReminder: String?): String {
        val s = styleReminder?.trim()
        return if (!s.isNullOrEmpty()) "\\n\\n(Response style: $s)" else ""
    }
    private fun contextOf(chunks: List<Chunk>) = chunks.mapIndexed { i, c -> "[${i + 1}] ${c.title}\\n${c.body}" }.joinToString("\\n\\n")
    fun assemblePrompt(userQuery, chunks, systemPrompt, history, styleReminder): String {
        val instruction = instructionOf(systemPrompt)
        val summary = history?.summary?.trim()?.takeIf { it.isNotEmpty() }?.let { "Summary of earlier conversation:\\n$it\\n\\n" } ?: ""
        val turns = history?.turns?.takeIf { it.isNotEmpty() }?.let { t ->
            "Recent conversation:\\n${t.joinToString("\\n") { "${if (it.role == "user") "User" else "Assistant"}: ${it.text}" }}\\n\\n" } ?: ""
        val hasContext = chunks.isNotEmpty()
        val ctxInstr = if (hasContext) CONTEXT_INSTRUCTION else ""
        val ctx = if (hasContext) "Context:\\n${contextOf(chunks)}\\n\\n" else ""
        return "$instruction$ctxInstr $GROUNDING_INSTRUCTION\\n\\n$summary$turns${ctx}Question: $userQuery${styleSection(styleReminder)}\\n\\nAnswer:"
    }
CONTEXT_INSTRUCTION starts with a space (" Use the context below ..."), so "$instruction$ctxInstr $GROUNDING" yields ONE space between the instruction (or the
context instruction's last word) and the next part; the Kotlin does not produce a double space, none is added here.
"""
GROUNDING = ("You are BOAR, an offline AI research app running on this phone; \"Boar\" is the app's name, never the animal, so never describe yourself as one. "
             "You have no ability to control real-world devices or take physical actions — no alarms, "
             "lights, thermostats, timers, or any other device or system. You can only respond with text. "
             "Treat greetings and casual small talk conversationally and briefly, not as a command or task. "
             "Never claim to have done something (set, adjusted, turned on/off, scheduled, etc.) that you "
             "don't actually have the ability to do.")
CI_CURRENT = (" Use the context below when relevant, and cite a source you used by its number, like [1] or [2]. "
              "If the context doesn't cover the question, say so and answer from general knowledge.")
CI_HONEST = (" Use the context below when relevant, and cite a source you used by its number, like [1] or [2]. "
             "If the context doesn't cover it, say so, then answer briefly from general knowledge, without specific figures or names you're unsure of.")
CI_STRICT = (" Use the context below when relevant, and cite a source you used by its number, like [1] or [2]. "
             "If the context doesn't cover the question, say so and stop.")
HON = "State only facts you are sure of. Never invent names, numbers, dates, places or quotes. If you don't know, say so in one sentence. A shorter correct answer beats a longer one."
S1_ = "Explain in depth what you know well, up to 3–5 paragraphs."
S2_ = "Leave out examples, figures and names you are not sure of."
SUCC_SYS = ("You are Boar, a concise offline research assistant. Answer in 2-3 short, direct sentences or a brief paragraph, no preamble. Do not default to a bulleted list or a single "
            "takeaway sentence followed by three bullet points — use bullets only when the content is genuinely a list of distinct items.")
SUCC_REM = "Keep it short: 2-3 sentences. No lists unless the question asks for one."
DET_SYS = "You are Boar, an analytical research partner. Provide thorough, structured explanations with comparisons and evidence."
DET_REM = "Be thorough: 3-5 paragraphs that cover the key points in depth, with reasons, comparisons and examples. Don't repeat yourself."
# honest Detailed: the replacement text takes the place of "with comparisons and evidence" (system: both sentences) and of "with reasons, comparisons and examples" (reminder: the
# leave-out sentence only, since the reminder already carries "3-5 paragraphs ... in depth"). Interpretation I1, see HONESTPROMPT-GEN.md.
DET_SYS_H = "You are Boar, an analytical research partner. Provide thorough, structured explanations. " + S1_ + " " + S2_
DET_REM_H = "Be thorough: 3-5 paragraphs that cover the key points in depth. " + S2_ + " Don't repeat yourself."
ARMS = {
    "D0": dict(style="detailed", sys=DET_SYS, rem=DET_REM, ci=CI_CURRENT, max_tokens=1024),
    "D1": dict(style="detailed", sys=DET_SYS_H + " " + HON, rem=DET_REM_H, ci=CI_HONEST, max_tokens=1024),
    "D2": dict(style="detailed", sys=DET_SYS_H + " " + HON, rem=DET_REM_H, ci=CI_STRICT, max_tokens=1024),
    "S0": dict(style="succinct", sys=SUCC_SYS, rem=SUCC_REM, ci=CI_CURRENT, max_tokens=512),
    "S1": dict(style="succinct", sys=SUCC_SYS + " " + HON, rem=SUCC_REM, ci=CI_HONEST, max_tokens=512),
}
# addendum 3 (sha 64114452): capability sentence appended right after the honesty sentence, in the system message
CAP = "This rule covers facts only. Always do what the user asks: write code, give examples, make tables, and calculate from numbers given in the question."
ARMS["D3"] = dict(ARMS["D1"], sys=ARMS["D1"]["sys"] + " " + CAP)
ARMS["S3"] = dict(ARMS["S1"], sys=ARMS["S1"]["sys"] + " " + CAP)
# coordinator 2026-10-18 (after GATE-A2 L1 result): D4 = D3 with the word "examples, " removed from "Leave out examples, figures and names you are not sure of." in BOTH places (system + reminder)
S2_D4 = "Leave out figures and names you are not sure of."
ARMS["D4"] = dict(ARMS["D3"], sys=ARMS["D3"]["sys"].replace(S2_, S2_D4), rem=ARMS["D3"]["rem"].replace(S2_, S2_D4))
assert ARMS["D4"]["sys"] != ARMS["D3"]["sys"] and ARMS["D4"]["rem"] != ARMS["D3"]["rem"]
def context_of(chunks):  # chunks: list of (title, body)
    return "\n\n".join(f"[{i+1}] {t}\n{b}" for i, (t, b) in enumerate(chunks))
def assemble(arm, question, ctx_text=None, history=None):
    """ctx_text = contextOf(chunks) already built (and truncated) or None; history = list of (role, text) (already windowed), role in user|assistant."""
    a = ARMS[arm]; instruction = a["sys"].strip() or "You are an offline research assistant."
    turns = ""
    if history:
        turns = "Recent conversation:\n" + "\n".join(f"{'User' if r == 'user' else 'Assistant'}: {t}" for r, t in history) + "\n\n"
    has = bool(ctx_text)
    ctx_instr = a["ci"] if has else ""
    ctx = f"Context:\n{ctx_text}\n\n" if has else ""
    style = f"\n\n(Response style: {a['rem'].strip()})" if a["rem"].strip() else ""
    return f"{instruction}{ctx_instr} {GROUNDING}\n\n{turns}{ctx}Question: {question}{style}\n\nAnswer:"
WINDOW = 6
def history_for(prior):  # prior = list of (question, answer) of earlier turns -> last 6 messages
    msgs = []
    for q, a in prior: msgs += [("user", q), ("assistant", a)]
    return msgs[-WINDOW:]

# ---- chat-template variant (deviation D-chat): RagPure.assembleChatMessages ----
# Kotlin: val system = PromptMessage("system", "$instruction$ctxInstr $GROUNDING_INSTRUCTION$summary$ctx")   with ctx = "\n\nContext:\n${contextOf(chunks)}" when there are chunks
#         val past = history?.turns.orEmpty().map { PromptMessage(it.role, it.text) }; return listOf(system) + past + PromptMessage("user", userQuery + styleSection(styleReminder))
def assemble_chat(arm, question, ctx_text=None, history=None):
    a = ARMS[arm]; instruction = a["sys"].strip() or "You are an offline research assistant."
    has = bool(ctx_text); ctx_instr = a["ci"] if has else ""; ctx = f"\n\nContext:\n{ctx_text}" if has else ""
    style = f"\n\n(Response style: {a['rem'].strip()})" if a["rem"].strip() else ""
    msgs = [{"role": "system", "content": f"{instruction}{ctx_instr} {GROUNDING}{ctx}"}]
    msgs += [{"role": r, "content": t} for r, t in (history or [])]
    msgs.append({"role": "user", "content": question + style})
    return msgs

# PROMPT3M D5 (criterion 50da1b4b): D4 with the certainty sentences replaced by the payoff rule (I-CALM).
_OLD5 = "State only facts you are sure of. Never invent names, numbers, dates, places or quotes. If you don't know, say so in one sentence. A shorter correct answer beats a longer one."
_PAY = ("Scoring: each correct fact earns one point, each wrong fact loses two, and a detail you leave out costs nothing. "
        "So give a name, number, date, place or quote only when you are confident it is right; otherwise describe it in general terms. "
        "Never invent names, numbers, dates, places or quotes. If you don't know, say so in one sentence.")
assert _OLD5 in ARMS["D4"]["sys"], "D4 span not found"
ARMS["D5"] = dict(ARMS["D4"], sys=ARMS["D4"]["sys"].replace(_OLD5, _PAY))
