---
name: "analise-artigo-cientifico"
description: "Análise crítica de artigos científicos e de perguntas clínicas baseadas em evidência para o Giovanni (médico). Use sempre que ele enviar um artigo, PDF, DOI, PMID ou link de estudo, pedir \"analise este estudo\", perguntar se uma conduta/terapia/exame \"funciona\", pedir nível de evidência, GRADE, comparação de diretrizes, ou resumo de estudo — mesmo que não diga \"análise crítica\"."
---

# Análise de artigo científico / pergunta clínica

Lineage: origin=gui; base=bacc7b719b48640060f5b235d5c5cb43d9ea2c2d

Objetivo: entregar uma leitura crítica que ele possa usar na prática e treinar como raciocínio, sem inventar dados. Ele é médico (emergência/pré-hospitalar, futuro radiologista); escreva em nível de pós-graduação, didático, com mecanismos e tamanhos de efeito.

## 1. Calibrar profundidade
- **Flags dele têm prioridade** sobre a calibração automática abaixo: `!!` → veredito direto em até 5 linhas, 1 fonte principal com ano e a certeza GRADE em uma linha (ofereça a análise completa); `***` → protocolo completo das seções 2–6, nível doutorado; `...` → estrutura de artigo da seção 3 (motivação, métodos, resultados, força estatística, pontos fortes/fracos, sinais vermelhos).
- Pergunta rápida ou vaga (ex.: "esse estudo presta?") → modo curto, ~300–600 palavras sem contar a lista de fontes: (a) qual estudo assumiu, se não foi dito, em uma linha; (b) veredito em 1–2 frases; (c) tabela pequena com efeito relativo, diferença absoluta e intervalo de confiança dos desfechos principais; (d) certeza GRADE provisória por desfecho em uma linha cada; (e) divergência Brasil/Europa/EUA em 2–3 linhas; (f) conduta prática; (g) fontes. Ofereça a análise completa no final em vez de fazê-la.
- Artigo enviado, pedido de profundidade ou evidência contestada → protocolo completo abaixo.
- Responda no idioma em que ele escreveu.
- Se a skill bias-risk-triage também carregar, ela só define a profundidade mínima de verificação; a estrutura e o formato são os desta skill.
- Dose, diluição, infusão, escores/calculadoras e conduta prática sem pedido de avaliação de evidência → use consulta-clinica; esta skill cuida de artigos, "isso funciona?" e nível de evidência.

## 2. Obter e verificar a fonte (antes de analisar)
1. Leia o texto completo quando possível (PDF enviado, PubMed/PMC). Se só houver resumo, diga isso explicitamente: análise de resumo não permite julgar risco de viés com segurança.
2. Checagem de integridade (registre o resultado, mesmo que "nada encontrado"):
   - Retratação / expressão de preocupação: notas no PubMed ("Retracted Publication", "Retraction in", "Expression of Concern") e no site da revista; base Retraction Watch (integrada ao Crossref).
   - Revista: indexação real (MEDLINE/PubMed, DOAJ para acesso aberto), sinais de revista predatória ou sequestrada (prazos de revisão irreais, taxa agressiva, editor fora da área). Critérios: Think. Check. Submit.
   - Registro prospectivo (ClinicalTrials.gov, ReBEC, DRKS, WHO ICTRP): desfecho primário registrado = publicado? Troca de desfecho é sinal vermelho.
   - Conflitos de interesse e financiamento; papel do patrocinador na análise.
   - Plausibilidade: efeito grande demais para a intervenção, amostra muito pequena, interrupção precoce por benefício, p-valores agrupados logo abaixo de 0,05, dados "bonitos demais".
3. Nunca complete dados ausentes. Se um número não está na fonte, escreva "não reportado".
4. Rastreabilidade de números: marque [primária] (texto completo/resumo do artigo), [sec] (resumo de terceiros: blogs de journal club, revisões) ou [calc] (calculado por você a partir de dados publicados). Se duas fontes secundárias divergirem, não escolha uma: mostre as duas ou omita e diga por quê. Graus de recomendação de diretrizes que você não leu na fonte vão como "não verificado".
5. Se o texto completo não abrir, diga logo no início que a análise de risco de viés é provisória.

## 3. Estrutura da análise (artigo único)
Use tópicos concisos, siglas escritas por extenso na primeira vez (ex.: "razão de risco (hazard ratio, HR)").

1. **Referência**: autores, revista, ano, DOI/PMID, desenho, registro.
2. **Motivação**: lacuna que o estudo pretende responder; PICO (população, intervenção, comparador, desfecho) explícito.
3. **Métodos**: desenho, alocação/mascaramento, tamanho amostral e cálculo de poder, desfecho primário (objetivo vs subjetivo/relatado pelo paciente), análise (intenção de tratar vs por protocolo), seguimento.
4. **Resultados**: efeito no desfecho primário com intervalo de confiança; sempre traduzir para efeito absoluto (redução absoluta de risco, número necessário para tratar/causar dano) quando houver dados; secundários e segurança separados. Separe desfechos objetivos (mortalidade, eventos adjudicados) de subjetivos (dor, qualidade de vida) e diga se o mascaramento protege os subjetivos.
5. **Força estatística**: precisão do intervalo de confiança frente a um limiar clinicamente relevante; multiplicidade; fragilidade quando aplicável; análise bayesiana/sensibilidade se houver.
6. **Risco de viés** com a ferramenta certa (ver references/ferramentas.md): RoB 2 para ensaio randomizado, ROBINS-I (v2) para estudo não randomizado de intervenção, QUADAS-2 para acurácia diagnóstica, AMSTAR 2 para revisão sistemática, PROBAST para modelos de predição.
7. **Pontos fortes e fracos** metodológicos e de execução.
8. **Certeza da evidência (GRADE)** para o desfecho principal — ver seção 4.
9. **Contexto**: o que diretrizes atuais dizem (ver seção 5) e se este estudo muda algo.
10. **Conclusão prática** em 2–3 linhas, com o grau de incerteza.
11. **Fontes**: lista com ano e link/DOI.

## 4. GRADE (aplicar ao corpo de evidência por desfecho)
- Ponto de partida: ensaios randomizados = alta; observacionais = baixa (ou alta se avaliados com ROBINS-I, que já incorpora confusão).
- Rebaixar (1 ou 2 níveis cada): risco de viés, inconsistência, evidência indireta, imprecisão, viés de publicação.
- Imprecisão: use a abordagem por intervalo de confiança em relação a limiares definidos (GRADE 34, 2022; GRADE 41, 2025 — "limiares escolhidos" em vez de categorias de contextualização). Se o intervalo cruza o limiar de importância, rebaixe; se não cruza mas o efeito é grande com amostra pequena, cheque o tamanho ótimo de informação.
- Elevar (principalmente observacionais): efeito grande, gradiente dose-resposta, confundimento residual que reduziria o efeito observado.
- Diga o motivo de cada rebaixamento. Expresse o resultado como "certeza alta/moderada/baixa/muito baixa de que o efeito verdadeiro está acima/abaixo de [limiar]".
- Para um único estudo, diga que GRADE se aplica ao corpo de evidência e faça uma avaliação provisória.

## 5. Busca e diretrizes
- Hierarquia: diretrizes atuais e revisões sistemáticas → ensaios randomizados → observacionais. Prefira a fonte mais recente; informe o ano.
- Busque em inglês e também em português e alemão quando houver fontes relevantes (ex.: diretrizes AWMF, Deutsches Ärzteblatt, sociedades brasileiras, SciELO).
- Quando recomendações divergirem entre Brasil (Ministério da Saúde, CONITEC, sociedades), Alemanha/Europa (AWMF, ESC, ERC, EMA) e EUA (AHA, ACR, USPSTF, FDA), mostre a divergência e o motivo provável.
- Notícias: confirme em veículo confiável e na fonte primária antes de relatar.

## 6. Separar fonte de raciocínio
Marque o que é dado da fonte e o que é sua inferência ("Interpretação:"). Se a conclusão parecer estranha, reavalie de forma ampla antes de responder.

## 7. Formato para resumos de estudo
Quando ele pedir resumo (não análise completa): tópicos curtos, siglas por extenso, efeito absoluto + intervalo de confiança + certeza, uma linha de limitação principal.