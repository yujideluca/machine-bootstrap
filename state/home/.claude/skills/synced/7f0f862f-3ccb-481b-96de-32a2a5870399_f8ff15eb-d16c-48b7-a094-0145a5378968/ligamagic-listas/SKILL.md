---
name: "ligamagic-listas"
description: "Use ao trabalhar com a Lista de Compras ou o Compra por Lista da LigaMagic - extrair cartas, gerar listas com edição, remover ou editar itens em lote. Para refazer ou conferir o carrinho por loja nos sites das lojas, use ligamagic-replicar-carrinho-nas-lojas."
---

# LigaMagic: listas e carrinho

Interop: role = domain; owns = formato do Compra por Lista e manuseio da Lista de Compras; defers to = browser-automacao-segura (ações em lote), ligamagic-replicar-carrinho-nas-lojas (carrinho por loja e montagem nos sites das lojas); honors = idioma da mensagem, flags !! *** ...

Antes de ações em lote no navegador, siga também a skill `browser-automacao-segura`.

## Formato do Compra por Lista (?view=cards/lista)
Uma carta por linha: `[Quantidade] [Card] [TAGS]`. Tags aceitas (confirmadas no site):
- Edição: `[EDICAO=PIP]` (sigla da edição, ex.: M10, MH3, PIP)
- Qualidade mínima: `[QUALIDADE=NM]` (M, NM, SP, MP, HP, D)
- Idioma: `[IDIOMA=PT]`, `[idioma=en]`; omita para "Qualquer idioma"
- Extras: `[EXTRAS=FOIL]`, `[extras=textless, fnm]`

Exemplo: `1 Command Tower [EDICAO=PIP] [QUALIDADE=NM]`
Use o nome em inglês. Terrenos numerados funcionam assim: `1 Forest (#0326) [EDICAO=PIP]`.
Sintaxes como `[PIP]`, `(PIP)` ou `|PIP` NÃO funcionam.
Para conferir, cole a lista e clique em "Detalhar Características": a coluna Edição deve vir preenchida.

## Lista de Compras (?view=mp/carrinho&open=1)
A mesma página tem duas estruturas: a Lista de Compras (tabela, abaixo) e o carrinho por loja (blocos `.pad-bot-10` com `div.row` e `input.qty`, um bloco por loja). O carrinho por loja é tratado pela skill `ligamagic-replicar-carrinho-nas-lojas`.
- A tabela de itens é `document.querySelectorAll('table')[0]`. Por linha: `input[type=number]` (quantidade) e selects (edição, qualidade, idioma, extras). O nome aparece em `cells[0]`, com o nome em inglês na última linha.
- A primeira linha com selects é a de "Aplicar Valores", não uma carta.
- O texto da edição selecionada tem o formato `SIGLA - Nome` (ex.: `PIP - Fallout`).
- O botão de remover é `.btn-circle.remove`. A remoção é imediata no servidor (aparece um aviso "foi removido da sua Lista de Compras"). Durante o processamento, o botão vira um spinner. O carrinho por loja usa a mesma classe: confira em qual estrutura o botão está antes de clicar.
- Clicar duas vezes no mesmo item em processamento gera o alerta "Ops! Não foi possível realizar a operação", que trava o navegador. Remova um por vez e espere a linha sumir.
- O `javascript_tool` pode falhar com seletores contendo certas strings ou com saídas longas. Use `querySelectorAll('table')[0]`, guarde resultados em `window.*` e leia em blocos de ~1000 caracteres.
- O cabeçalho mostra "Total: N cards", que soma as quantidades.