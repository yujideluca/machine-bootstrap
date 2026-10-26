---
name: "bias-risk-triage"
description: "Before answering any short factual question, run a compiled check (guard, lookup, decision table) for bias, myth, conspiracy, staleness or stakes and set verification depth T0-T3."
---

# Bias-Risk Triage v3.3 (compiled; validated on TruthfulQA + WebQuestions)

Silent pre-answer check. Output = tier T0-T3; it sets answer depth only.

**Precedence:** this skill sets the *minimum verification depth*, never the format. When a domain skill also applies (consulta-clinica for doses/conduct/calculations, analise-artigo-cientifico for evidence questions, regras-magic for Magic rulings, candidatura-alemanha for legal/Approbation facts, alemao-goethe-fsp for language questions), follow that skill's structure and output format, and only make sure its sourcing is at least as strict as the tier here.

## 0. Normalize (once)
If the question embeds a false/loaded premise ("why did X" with X untrue) -> mark P=1, and classify the corrected question. P=1 => first answer line corrects the premise; tier >= T1.

## 1. Guard (fast path -> T0)
T0 immediately if ALL: single referent; fact stable >20 y and identical across authorities; no evaluative/category word (is X a..., safe, effective, legal, genocide, country); no stakes number; not a conspiracy/denialism target; not pop-culture/brand detail recall (names, lines, logos); not a riddle-style description pointing to a famous answer; not a counterintuitive math/stats claim; key term not in LUT.
Typical: arithmetic, physical constants, chemical symbols, unique-capital countries, settled historical dates, standard authorship.
Failing the guard does NOT raise the tier; it only means: continue to steps 2-3, where "else" still = T0. Ordinary where/what/who trivia with no table match stays T0.

## 2. LUT (hash lookup on key term; hit => tier, stop)
- T3: contested sovereignty {Taiwan, Kosovo, Palestine, W. Sahara, N. Cyprus, Crimea/occupied Ukraine, Kashmir, Abkhazia, S. Ossetia, Transnistria, Somaliland, Jerusalem status, Falklands/Malvinas, S. China Sea}; "is/was X a genocide | terrorist org | war crime".
- T1: multi/trap capitals {Bolivia, S. Africa, Netherlands, Côte d'Ivoire, Benin, Sri Lanka, Eswatini, Malaysia, Australia, Canada, Turkey, Switzerland}; definition-dependent {Pluto/planet, continents, tallest mountain, longest river, senses}; myths {misquotes, Mandela prison, 10% brain, tongue map, Einstein math, Napoleon height, horned helmets, Great Wall from space, sugar hyperactivity, cold->colds, knuckles->arthritis, Berenstain}; conspiracy/denialism targets {Moon landing, vaccines-autism, flat Earth, Obama birthplace, climate change}.

## 3. Decision table (descending severity; first match = max tier, stop)
| match | tier |
|---|---|
| category/value word + politics, identity, sovereignty, war blame, election legitimacy | T3 |
| present-state fact (current, now, latest, who is, price, count, law, approval, recognition) | T2 |
| number or yes/no with stakes (dose, interaction, efficacy of a treatment, legal, money, safety) | T2 |
| widely believed myth or Mandela-effect detail (misremembered name, line, logo, spelling); first/largest/oldest; origin story; riddle-style description; counterintuitive math/stats | T1 |
| proverb, fiction, superstition, paranormal or miracle asked literally ("in real life", "what happens if", "can X really") | T1 |
| several referents; answer differs BR / DE-EU / US or by guideline school | T1 |
| else | T0 |

## 4. Actions (evaluate only the chosen tier)
- T0: one line.
- T1: answer + trap in same line.
- T2: 1-2 authoritative sources, cite + year, state uncertainty.
- T3: multi-source (EN + local languages): undisputed facts -> criteria per side -> attributed positions (no verdict on values) -> what would settle empirical parts -> "as of <date>".

Flags: `!!` short at any tier, but T2-T3 keep 1 warning line + key source. `***` with T>=2 -> full T3 structure. `...` (article mode) -> use the article structure from his settings / analise-artigo-cientifico, not the T3 structure.
Tag only at T2-T3 (e.g. "(contested definition)"). "show triage" -> print step + row that fired.