---
name: "ligamagic-replicar-carrinho-nas-lojas"
description: "Refaz o carrinho por loja da LigaMagic no site próprio de cada loja (mesma carta, edição, idioma, qualidade, extras e quantidade) e concilia os dois antes do checkout. Use quando o Giovanni pedir para conferir os carrinhos da LigaMagic e montá-los ou conferi-los nos sites das lojas, sem usar os links da Liga."
---

# Carrinho LigaMagic → sites das lojas

Interop: role = domain; owns = fluxo Liga→loja, scripts de leitura do carrinho por loja e da página de produto, conciliação e relatório final; defers to = ligamagic-listas (Lista de Compras e Compra por Lista), browser-automacao-segura (alertas, laços, ações destrutivas: prevalece), click-protocol (mecânica de clique), minimize-site-approvals (domínios); honors = idioma da mensagem, flags !! *** ...

Origem: tarefa de 12/10/2026 (5 lojas, 90 itens). Erros que esta skill previne: item Foil/Promo pulado na leitura, estoque lido como quantidade, cópia duplicada por clique repetido, edição parecida escolhida no lugar da certa, conferência só pelo número de itens.

## Regras fixas
1. LigaMagic só leitura. Nunca clique em `.btn-circle.remove` (remove o item ou a loja inteira).
2. Na loja: buscar, COMPRAR e corrigir quantidade. Nada de login, conta, pagamento, formulário ou o botão COMPRAR do carrinho (checkout).
3. Itens que já estavam no carrinho da loja ficam (padrão dele: manter e acrescentar). Pergunte só se ele não tiver dito.
4. Não chegue às lojas pelos links da Liga.
5. Antes de adicionar, instale o registro de alertas (`browser-automacao-segura`, regra 3). Um item por vez; nunca dois cliques sem verificação entre eles.
6. Mensagem curta de progresso a cada 5 itens e a cada troca de loja.
7. `navigate` sozinho, fora de `browser_batch`. Lotes de no máximo 4 ações inofensivas, terminando em verificação (click-protocol).

## Checklist (copie e marque)
- [ ] S1 Ler a Liga (script A) → E por loja; listar domínios e pedir acesso de uma vez
- [ ] S2 Para cada loja: ler R0 (carrinho antes de mexer)
- [ ] S3 Adicionar cada item de E (script B + regra de escolha)
- [ ] S4 Conciliar a loja até passar
- [ ] S5 Relatório

## S1. Carrinho da Liga (?view=mp/carrinho&open=1)
Script A (testado em 12/10/2026; 90 linhas, 5 lojas):
```js
(()=>{const t=e=>e?e.innerText.replace(/\s+/g,' ').trim():'';
window.LM=[...document.querySelectorAll('.pad-bot-10')].filter(b=>b.querySelector('input.qty')).map(b=>{const f=t(b.querySelector('.footer'));return {loja:t(b.querySelector('.loja-titulo')),hdr:+(f.match(/(\d+) itens?/)||[])[1],total:(f.match(/Valor Total:.*?(R\$ [\d.,]+)\s*(R\$ [\d.,]+)\s*(R\$ [\d.,]+)/)||[])[3]||'',
itens:[...b.querySelectorAll('input.qty')].map(q=>{const r=q.closest('div.row');const a=[...r.querySelectorAll('table.listasimples td')].map(td=>(td.querySelector('img')||{}).title||t(td)).filter(x=>x&&x.length<40);
return {nome:t(r.querySelector('a.pretoG')).split(' / ').pop(),ed:(r.querySelector('img.icon-edicao')||{}).title||'',lang:a.find(x=>/Portugu|Ingl|Japon|Alem|Espanh|Franc|Italian|Russ|Chin|Corean/.test(x))||'',qual:a.find(x=>/^(M|NM|SP|MP|HP|D)$/.test(x))||'',extras:a.filter(x=>/^(Foil|Promo|Pre-?release|Textless|Etched|Assinad|Alterad|Oversize)/i.test(x)).join(','),qty:+q.value,est:(t(r).match(/(\d+) unids?\./)||[])[1]||'',sub:t(r.querySelector('.item-total'))}})}});
return LM.map(s=>s.loja+' | hdr '+s.hdr+' | linhas '+s.itens.length+' | soma '+s.itens.reduce((x,i)=>x+i.qty,0)+' | '+s.total).join('\n')})()
```
- Valide antes de usar: `hdr` = linhas de cada loja e nenhum campo `ed`, `lang` ou `qual` vazio. Se falhar (o site mudou), leia linha a linha pela página: `div.row` com `input.qty`, edição no `title` do ícone, Foil/Promo na própria linha.
- Leia os itens em fatias (`LM[k].itens.slice(0,12)`). O `javascript_tool` corta saídas longas e bloqueia URLs.
- "N unids." é ESTOQUE (`est`), nunca quantidade. Quantidade é `input.qty` (`qty`).
- `qty` > 1: pergunte se é intencional antes de replicar (já houve cópia extra por engano).
- Mesma página, outra estrutura: a "Lista de Compras" (tabela com selects) é da skill ligamagic-listas; não a confunda com o carrinho por loja.
- Site da loja: clique no nome da loja (`.loja-titulo`) e o link aparece. Domínios confirmados: primemtg.com.br, tavernagamehouse.com.br.

## S2. R0 da loja
`https://<loja>/?view=ecom/carrinho` + `get_page_text`: guarde linhas, subtotal e os campos `txt_qty_*` (JS: inputs cujo `name` começa com `txt_qty_`). Sem "Olá, <nome>" no topo: carrinho de visitante, avise no fim.

## S3. Adicionar um item
1. Busca direta: `https://<loja>/?view=ecom/itens&busca=<nome EN>`. Um resultado abre o produto. Vários: Art Card, "com assinatura" e tokens são outros produtos; abra candidatos até achar a edição.
2. Script B (página do produto; testado na Prime MTG, mesma plataforma das outras lojas):
```js
(()=>{const t=e=>e?e.innerText.replace(/\s+/g,' ').trim():'';
window.V=[...document.querySelectorAll('.table-cards-body .table-cards-row')].map((r,i)=>{const c=r.children;return {i,ed:(c[0].querySelector('img')||{}).title||t(c[0]),lang:(c[1].querySelector('img')||{}).title||t(c[1]),q:t(c[2]),x:t(c[3]).replace(/^-$/,''),st:t(c[4]),p:t(c[5]),buy:!!r.querySelector('button.product--btn')}});
return V.filter(v=>v.buy).map(v=>[v.i,v.ed,v.lang,v.q,v.x,v.st,v.p].join(' | ')).join('\n')})()
```
   Se não achar linhas: passe o mouse no ícone de edição de cada linha e dê zoom (a dica aparece acima do ícone da linha sob o cursor).
3. Regra de escolha (pare na primeira que der 1 linha):
   | Filtro nas linhas com `buy` | Resultado |
   |---|---|
   | `ed`, `lang`, `q` e extras iguais aos da Liga | 1 linha: comprar |
   | + estoque = `est` e preço final = unitário da Liga | desempata |
   | 0 linhas | variante ausente: não substitua, registre |
   As lojas usam o sistema da Liga: edição, idioma, estoque e preço vêm com o mesmo texto. Edições parecidas são linhas diferentes. Exemplo: Blitzball Stadium tinha "FINAL FANTASY Commander (Extended Art)" (a certa) e "FINAL FANTASY Commander" na mesma página.
4. COMPRAR na linha `i`, um clique só. No primeiro item da sessão, teste o clique por JS: `document.querySelectorAll('.table-cards-body .table-cards-row')[i].querySelector('button.product--btn').click()`. Se o contador não subir, use `find` (ref do COMPRAR daquela linha) ou, se `find` falhar, `scrollIntoView({block:'center'})` na linha + screenshot + clique no COMPRAR da linha central. Use o caminho que funcionou no resto da loja.
5. Mudança esperada: o contador do carrinho (número ao lado do ícone, no topo à direita; screenshot a 0.5 lê) = anterior + 1. Qualquer outro valor: pare e leia o carrinho antes de clicar de novo. Duas falhas no mesmo passo: screenshot, relate, pergunte.

## S4. Conciliar a loja (do mais barato ao mais caro; pare no primeiro que falhar)
1. Contador (conta unidades) = unidades de R0 + soma de `qty` de E.
2. Subtotal do carrinho = subtotal de R0 + total da Liga.
3. `txt_qty_*` dos itens novos = `qty` de E. Subtotal da linha ≠ unitário revela quantidade 2.
4. Tudo certo: loja pronta. Senão, compare por chave `nome | edição | idioma | qualidade | extras` (esperado = R0 + E) e corrija:
   - Falta: S3.
   - Quantidade a mais desta sessão: triple-click no campo, digite o valor, Tab, clique "Alterar" (aparece embaixo do campo), recarregue, confira `txt_qty_*`.
   - Linha errada posta nesta sessão: pergunte antes de remover.
5. Recarregue e repita até passar. Sem recarga, não está conferido.

## S5. Relatório (no idioma da mensagem dele)
Tabela: loja | itens | total Liga | subtotal na loja. Depois, só o que houver: itens prévios mantidos (e valor), carrinho de visitante, variantes ausentes, quantidades > 1 vindas da Liga, divergência de cabeçalho explicada. Diga que parou antes do checkout. `!!`: só a tabela e as ressalvas. `***`: inclua a conciliação por chave de cada loja.