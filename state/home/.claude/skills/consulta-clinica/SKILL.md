---
name: "consulta-clinica"
description: "Respostas clínicas rápidas e cálculos de dose para o Giovanni (médico de emergência/pré-hospitalar): conduta, dose, diluição, infusão, escores, calculadoras, interações e suplementos — não para análise de artigo ou estudo."
---

# Consulta clínica

Lineage: origin=gui; base=e84b0a76232ca638950f72dda47804287d84d56a

Interop: role = domain; owns = formato de respostas clínicas e de cálculo; defers to = analise-artigo-cientifico (artigo, estudo, "isso funciona?" com pedido de evidência aprofundada), bias-risk-triage (só profundidade mínima de verificação); honors = idioma da mensagem, flags !! *** ...

## Template (sempre nesta ordem)
**Conduta:** <ação + dose/resultado final em 1–2 linhas — o número que ele vai usar vem aqui>
**Especialidade / diretriz:** <especialidade responsável> — <diretriz da escola dessa especialidade, edição/ano; confira a vigente>
**Dose:** <fármaco> <mg/kg ou mg> → <total em mg> <via>, <intervalo>, máx <x>
**Cálculo (conferido 2×):** <fórmula → variáveis com unidade → conta>
**Evidência:** <classe/nível ou certeza GRADE>
**BR × DE/EU × EUA:** <diferença que muda a conduta, se houver>
**Não verificado:** <o que não foi conferido na fonte>

Omita só Dose/Cálculo quando não houver dose ou conta; Especialidade/diretriz (com ano) e Evidência são obrigatórias. `!!` → só Conduta + Dose + diretriz em ≤5 linhas, mas o cálculo continua sendo conferido.

## Regras
- Fontes por especialidade: ressuscitação → AHA/ERC; cardiologia → AHA/ACC, ESC (SBC no Brasil); trauma pré-hospitalar → PHTLS; emergências clínicas pré-hospitalares → AMLS; asma → GINA; DPOC → GOLD; sepse → Surviving Sepsis Campaign; AVC → AHA/ASA, ESO; aorta (dissecção, aneurisma) → ESC 2024 (doença arterial periférica e aórtica), ACC/AHA 2022; pediatria → AHA PALS, ERC; clínica geral → Harrison 22ª ed. (2025) + diretriz mais recente.
- Dose em mg/mcg; sem concentração informada, não converta para mL. Se converter, declare a concentração usada.
- Cálculos e escores: escreva a fórmula/regra (e qual variante, ex. QTc Bazett vs Fridericia), monte a tabela de variáveis com unidades, faça a conta em Python quando houver ferramenta, e cheque a faixa (dose ≤ máxima; resultado 10× fora do habitual = refazer).
- Suplementos/nutrição: nível de evidência, posologia e valores nutricionais.
- Nunca invente número; o que não foi conferido vai em "Não verificado".

## Exemplo anotado
Pergunta: "Adrenalina na PCR de criança de 18 kg?"
**Conduta:** adrenalina 0,18 mg IV/IO o quanto antes, repetir a cada 3–5 min.
**Especialidade / diretriz:** ressuscitação pediátrica — AHA PALS 2025 e ERC 2025 (conferir edição vigente).
**Dose:** 0,01 mg/kg → 0,18 mg IV/IO, a cada 3–5 min (máx 1 mg/dose).
**Cálculo (conferido 2×):** 18 kg × 0,01 mg/kg = 0,18 mg; 0,18 ≤ 1 mg ✔.
(Concentração não informada → dose em mg, sem mL.)
**Evidência:** recomendação baseada em evidência limitada (observacional).
**BR × DE/EU × EUA:** sem diferença relevante de dose.