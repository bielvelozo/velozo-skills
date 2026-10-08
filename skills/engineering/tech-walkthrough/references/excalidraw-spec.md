# O quadro Excalidraw: spec, visual e disposição

O desenho inteiro é um quadro Excalidraw só, gerado por `scripts/excalidraw_build.py` a partir de um spec JSON. Você escreve o conteúdo (texto, ordem, cores); o script calcula posições, altura das seções, setas, legendas e a disposição em fileiras, e produz dois arquivos: `<slug>.excalidraw` (abre no excalidraw.com, VS Code, Obsidian) e `<slug>.html` (página com o Excalidraw embutido, pronta para publicar como artifact).

```bash
python <skill>/scripts/excalidraw_build.py docs/walkthroughs/<slug>.spec.json --out-dir docs/walkthroughs
```

Um spec completo de exemplo está em `examples/rastreio-whatsapp.spec.json`; copie a estrutura dele.

O nome dos arquivos de saída vem do nome do spec (`<slug>.spec.json` → `<slug>.excalidraw`, `<slug>.html`).

## Formato do spec

```json
{
  "title": "Tech walkthrough — <entrega>",
  "artifact": "https://claude.ai/artifact/...",
  "sections": [ ... ]
}
```

`artifact` fica vazio na primeira vez; depois de publicar, grave a URL aqui para as próximas execuções republicarem no mesmo link.

Cada seção tem `id`, `title`, `note` (uma ou duas frases, apagadas, abaixo do título), `row` (a fileira em que ela entra) e **um** destes três corpos:

### `flow`: fluxo vertical (antes, depois)

Só a lista de caixas, em ordem. O script centraliza, espaça, liga com setas e monta a legenda.

```json
{"id": "depois", "title": "Depois", "row": 1, "note": "...", "flow": [
  {"title": "Bling · pedido despachado", "subtitle": "nota emitida, rastreio gerado", "style": "gray"},
  {"title": "OMS · rota POST /webhooks/bling/shipment", "subtitle": "recebe o aviso e enfileira", "style": "green"},
  {"title": "Shopify · e-mail de rastreio", "subtitle": "continua igual", "style": "dashed"}
]}
```

- `style`: `gray`, `red`, `green`, `yellow`, `blue`, `dashed`. Caixa `dashed` recebe seta tracejada; `"arrow": "dashed"` força isso em qualquer caixa; `"arrowLabel"` põe um rótulo curto na seta que chega.
- `id` é opcional (vira `<seção>-<n>`); use quando uma seta de outra seção precisar apontar para a caixa.

### `stack`: fichas e tabelas empilhadas (peças, banco, performance, decisões, riscos)

Lista de itens de cima para baixo; o script calcula a altura de cada um pelo texto.

```json
{"id": "perf", "title": "Performance", "row": 3, "w": 960, "note": "Estimativa pela leitura do código.", "stack": [
  {"table": {"widths": [260, 140, 432], "header": ["Fluxo", "Veredito", "Por quê"], "rows": [
    ["Aviso de despacho", {"text": "novo, leve", "style": "green"}, "A rota só enfileira; o envio roda em segundo plano."]
  ]}},
  {"columns": [
    {"style": "yellow", "heading": "O que faria ficar lento", "text": "..."},
    {"heading": "Custo novo", "text": "..."}
  ]},
  {"card": {"style": "green", "heading": "O que muda", "text": "..."}}
]}
```

- `card`: ficha com `heading` (primeira linha) e `text`; `style` como nas caixas, `white` por padrão.
- `table`: `header` opcional, `rows`; uma célula pode ser `{"text", "style"}` para ter fundo colorido (etiqueta de veredito, "NOVO", gravidade). `widths` opcional; sem ele, colunas iguais.
- `columns`: fichas lado a lado, mesma altura.

### `boxes` + `arrows`: posicionamento manual (mapa da arquitetura, bastidores com ramificação)

Coordenadas relativas à seção. Margem de 64; conteúdo começa em `y: 152` quando a nota tem até duas linhas.

```json
{"id": "bast", "title": "Bastidores", "row": 1, "w": 896, "note": "...", "legend": {"red": "caso de falha"},
 "boxes": [
   {"id": "b1", "x": 160, "y": 152, "w": 400, "h": 88, "title": "Rota POST /webhooks/bling/shipment", "subtitle": "publica 1 mensagem", "style": "green"},
   {"id": "b3", "x": 160, "y": 440, "w": 400, "h": 88, "title": "Worker tracking-notifier (ECS)", "subtitle": "chama o Chatwoot", "style": "green"},
   {"id": "b5", "x": 616, "y": 440, "w": 216, "h": 88, "title": "Esgotou as 3 tentativas", "subtitle": "fica \"falhou\"", "style": "red"},
   {"id": "m0", "x": 288, "y": 136, "w": 320, "h": 432, "style": "dashed"}
 ],
 "arrows": [{"from": "b1", "to": "b3"}, {"from": "b3", "to": "b5", "label": "falhou"}, {"from": "b5", "to": "b4", "via": [[724, 628]]}],
 "labels": [{"x": 304, "y": 144, "text": "OMS"}]}
```

- Seta: o script escolhe as arestas pela posição relativa (abaixo → de baixo para cima; à direita → da direita para a esquerda). `via` dá pontos de dobra; `label` põe texto ao lado; `style: dashed`.
- Caixa sem `title` e `style: dashed` é um contêiner de sistema; o nome vai em `labels`.
- Tamanhos que funcionam: coluna principal 400×88 em `x: 160`, passo de 144; caixa lateral 216×88 em `x: 616`. Mapa: sistemas externos 160×80 em `x: 64` e `x: 672`, contêiner 320×432 em `x: 288`, peças internas 240×80 em `x: 328`, passo de 136.

### Campos comuns

- `w`: largura da seção (720 para `flow`, 896 para o resto por padrão; tabelas largas pedem 960–1120). `h` só se quiser forçar.
- `legend`: automática quando a seção usa duas ou mais cores; `false` desliga; `{"red": "caso de falha"}` troca o texto de uma cor.
- `x`, `y`: só para tirar a seção da fileira e posicioná-la à mão.

## Disposição no quadro

As seções entram nas fileiras pelo `row`, na ordem em que aparecem no spec, com 80px entre seções e 320px entre fileiras.

| `row` | Seções, da esquerda para a direita |
|---|---|
| 1 | Antes, Depois, Bastidores |
| 2 | Mapa da arquitetura, Peças tocadas |
| 3 | Banco de dados, Performance, Frontend |
| 4 | Como chegou nessa implementação, Riscos |

## Cores com significado fixo

| Estilo | Significado | Legenda automática |
|---|---|---|
| `gray` | já existe e não muda | "já existe, não muda" |
| `red` | onde está o problema hoje; caso de falha | "onde está o problema" |
| `green` | novo ou alterado | "novo ou alterado" |
| `yellow` | decisão, pendência, atenção | "decisão ou pendência" |
| `blue` | sistema externo em destaque (raro) | "sistema externo" |
| `dashed` | fora do fluxo, acontece depois, contêiner de sistema | "fora do fluxo, acontece depois" |

## Tamanho do texto

Caixa: título de até 4 palavras mais o nome técnico (~34 caracteres por linha em 440px), subtítulo de até 6 palavras. Ficha e célula: uma frase por célula; o script quebra o texto, mas uma célula de cinco linhas é sinal de que o conteúdo devia ser diagrama.

## A página HTML

O `<slug>.html` carrega React e o Excalidraw de CDN (unpkg, versões fixas) e embute o quadro como JSON; o viewer pode editar, exportar e salvar. Publique com a Artifact tool (`file_path` = o html, `icon: "diagram"`, uma frase em `description`); nas execuções seguintes passe também `url` com o valor de `artifact` do spec. A página é sempre clara, como o Excalidraw, mesmo com o viewer em modo escuro. A fonte manuscrita (Virgil, `scripts/Virgil.woff2`) vai embutida, porque o artifact bloqueia o download de fontes do CDN.
