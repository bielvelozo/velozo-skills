---
name: tech-walkthrough
description: Explica visualmente a parte técnica de um plano já decidido, num quadro Excalidraw único no estilo de desenho de system design (publicado como artifact e salvo como arquivo .excalidraw no repositório) — mapa da arquitetura, diagramas de antes e depois, o fluxo de bastidores (filas, workers, jobs, webhooks), rotas e serviços novos, packages instalados, migrations e o porquê de cada uma, o impacto em performance e os riscos que sobram (pontos de falha por gravidade, onde o conselho discorda do plano, o que resistiu) — quase sem texto no chat e sem assumir que o usuário lembra do código. A implementação explicada sai de um debate entre três sub-agentes (mínimo, robusto, performance) que convergem para a melhor opção. Use sempre que o usuário terminar um planejamento (grilling, /grill-me, /grill-with-docs, brainstorming, writing-plans, spec, issue) e quiser entender o que vai ser feito tecnicamente, ou disser coisas como "me explica a parte técnica", "o que vai mudar no código", "quero entender a implementação", "tem migration?", "isso vai ficar lento?", "raio-x técnico", "tech walkthrough", "desenha a implementação", "essa é a melhor implementação?", "o que pode dar errado?", "revisa o plano técnico", mesmo que não peça diagrama. Aceita o argumento `fast` para pular o debate em entregas pequenas.
---

# Tech walkthrough

O planejamento deixou as decisões de negócio claras. Falta o usuário enxergar **o que vai acontecer no código** antes de aprovar a implementação. Seu trabalho é mostrar isso de um jeito que ele entenda em dois minutos, olhando mais do que lendo.

O leitor é dono do produto e programa, mas **não tem o código na cabeça**. Ele não lembra o que cada pasta, package ou serviço faz. Se a explicação depender dessa memória, ela falhou.

A entrega é **um quadro Excalidraw só**, no estilo de system design: seções com caixas, setas, fichas e tabelas curtas, num campo infinito. Ele sai em dois formatos a partir do mesmo spec: uma página com o Excalidraw embutido, publicada como artifact (link), e o arquivo `.excalidraw` salvo no repositório. O chat recebe só o link e três linhas. Texto corrido no chat é sinal de que algo que devia ser desenho virou parágrafo.

## Antes de explicar: levante os fatos no código

Não explique a partir do plano sozinho. Leia o código que o plano toca (use sub-agentes Explore se for espalhado) até conseguir responder, para cada peça envolvida:

- Qual é a responsabilidade dela hoje, em uma frase de negócio?
- Como o fluxo afetado funciona hoje, do gatilho até o resultado?
- O que exatamente entra, sai ou muda?
- Quanto trabalho o fluxo faz hoje e quanto vai fazer depois: consultas ao banco, chamadas a serviços externos, o que roda na hora e o que roda em segundo plano, e com que volume de dados?
- Qual é o nome técnico real dela (nome da fila SQS, do worker ou Lambda, da rota, do package), lido no código ou na configuração de infraestrutura (CDK, Terraform, serverless, docker-compose, `.env`)? Os diagramas usam esse nome como título.
- Para tudo que roda em segundo plano: quem dispara, por onde passa (qual fila, qual agendamento), quem executa, em que ordem, quantas vezes tenta de novo, o que acontece quando desiste e onde o resultado fica registrado?

Se o plano deixa uma decisão técnica em aberto (qual lib, onde mora a função, se precisa de tabela nova), ela não é sua para escolher sozinho: é o conselho técnico abaixo que decide.

## Modo `fast`

`/tech-walkthrough fast` pula o conselho técnico. Use quando a entrega é pequena (uma rota, um campo, um ajuste num fluxo que já existe) e o plano não deixou decisão técnica em aberto; três agentes lendo código e debatendo seria desproporcional. Nesse modo você mesmo escolhe a implementação (levantando os fatos no código do mesmo jeito), a seção "Como chegou nessa implementação" tem uma linha dizendo que foi modo fast sem debate, e a seção de riscos sai de uma passada sua com a lista do agente Robusto abaixo. Todo o resto (quadro, seções, chat curto) é igual. Sem o argumento, o conselho roda sempre.

## Conselho técnico: três agentes escolhem a implementação

O plano fecha o negócio, mas quase sempre deixa a implementação em aberto: onde mora a função, fila nova ou reaproveitada, tabela ou campo livre, lib ou código próprio. Decidir isso sozinho, numa passada só, tende a produzir a primeira ideia que funciona, não a melhor. Por isso a escolha passa por um debate entre três sub-agentes com vieses diferentes, e o quadro explica a implementação que saiu do consenso.

Os prompts de todas as rodadas estão prontos em `references/council-prompts.md`; preencha as lacunas e mande como estão. Lance os três com a Agent tool numa única mensagem, em paralelo, depois de levantar os fatos no código. Cada um recebe o plano inteiro, os fatos que você levantou, acesso ao código (devem ler antes de afirmar) e o viés dele:

- **Mínimo**: a menor mudança que entrega o plano. Reaproveita o que existe, evita package e migration a não ser que seja inevitável, prefere a peça que já tem essa responsabilidade.
- **Robusto**: o que quebra em produção. É quem vai ser acordado às 3h quando isso falhar, e olha o código, não o plano. Procura especificamente: repetição e timeout (a chamada externa deu certo, mas a resposta se perdeu; a pessoa clica de novo ou o job tenta de novo; sequências "faz A → B → C" costumam ficar mais robustas como reconciliador, que lê o estado atual e executa só o que falta); assíncrono tratado como definitivo (operação externa que devolve "aceito" e pode falhar depois); corrida com o que já existe (filas, syncs e webhooks atuais que rodam antes ou depois do fluxo novo e desfazem o que ele fez, inclusive em retentativa, DLQ e reenvio manual); guarda faltando (código que deveria recusar o novo estado e não recusa); falha silenciosa ("não achei, ignoro"); e o que fica fora do código (processo humano, financeiro, e-mail ao cliente, permissão) que o plano supõe sem confirmar. Propõe a implementação que aguenta isso.
- **Performance**: carga e pico. Chamada externa no caminho de quem espera, consulta repetida em laço, busca sem índice, volume carregado. Propõe a implementação que continua boa com 10 vezes o volume de hoje.

Rodadas:

1. **Proposta**: cada agente devolve a implementação dele no mesmo esqueleto das seções (peças tocadas, banco, bastidores), em no máximo 40 linhas, com a justificativa de cada escolha e a lista das decisões em que ele acha que os outros dois discordariam.
2. **Crítica**: mande para cada agente, com SendMessage (mesmo agente, contexto preservado), as propostas dos outros dois. Ele responde o que aceita, o que mantém e por quê, e a proposta revisada. Crítica precisa apontar o fato do código ou o cenário concreto que sustenta a objeção; "eu prefiro" não conta.
3. Se depois da crítica ainda há divergência real, uma rodada a mais. Máximo de três rodadas. O que sobrar vira pendência na seção de riscos, com a posição de cada agente em uma linha.
4. **Riscos**: com a implementação fechada, cada agente devolve, em até 20 linhas, os pontos de falha que ainda sobram nela (ponto, gravidade com o dano em poucas palavras, situação) e as decisões que ele atacou e que resistiram. O Robusto lidera esta rodada; os outros dois acrescentam o que viram do ângulo deles.

Você consolida o consenso. Regras de desempate:

- Fato vence opinião: afirmação sobre o código que um agente fez e outro contestou, você confere antes de aceitar. Os pontos de falha de gravidade alta, confira você mesmo no código antes de desenhar.
- Empate de gosto vai para o Mínimo, a não ser que o Robusto mostre uma falha concreta ou o Performance mostre um gargalo concreto que a opção mínima não resolve.
- O que o plano já decidiu não se reabre em silêncio. Se um agente contesta uma decisão do plano, ela entra na seção de riscos como "o conselho discorda do plano", com o motivo, e a explicação segue o plano.

O usuário não vê o debate; vê o resultado em duas seções do quadro: "Como chegou nessa implementação" (as decisões em que o conselho pesou alternativas) e "Riscos" (o que ainda pode quebrar e o que resistiu). O debate é a auto-análise; não existe uma passada separada depois dele.

## Regra de linguagem: responsabilidade primeiro, nome depois

Toda peça de código é apresentada pelo que ela faz, e o nome técnico vem depois, entre crases, como referência.

- Ruim: "Vamos adicionar `resolveCpf()` em `packages/mirror`."
- Bom: "No package que mantém a cópia local dos pedidos da Shopify (`packages/mirror`), entra uma função que descobre o CPF do cliente (`resolveCpf`)."

O mesmo vale para tabelas ("a tabela que guarda um registro por cliente, `accounts`"), rotas, jobs e libs externas ("`bullmq`, uma fila para rodar tarefas em segundo plano com nova tentativa se falhar").

Nos diagramas a ordem se inverte. O título de cada caixa é o nome técnico real, o mesmo que o usuário vai encontrar no código, no console da AWS ou nos logs. O subtítulo, menor e mais apagado, diz em linguagem de negócio o que a peça faz. Assim ele aprende o nome e ao mesmo tempo entende a função.

- Ruim: título "Fila padrão", subtítulo "sem ordem, até 3 tentativas".
- Bom: título "SQS `orders-default`", subtítulo "fila sem ordem, até 3 tentativas".
- Bom: título "Worker `order-events` (ECS)", subtítulo "processa o pedido em segundo plano".

O título indica o tipo de infraestrutura e o nome do recurso: SQS, SQS FIFO, DLQ, Lambda, worker ECS, cron, rota `POST /...`, package `packages/...`, tabela `orders`. Tire esse nome do código ou da configuração de infraestrutura e nunca o invente. Se não achar, escreva o tipo seguido de "(nome não encontrado)". Sistemas externos usam o nome do produto (Shopify, Bling) e, no subtítulo, a API ou o evento ("webhook `orders/updated`"). Quando a mesma peça aparece duas vezes no fluxo, repita o mesmo título para o usuário perceber que é ela de novo.

## O quadro: onde tudo é desenhado

A resposta inteira vive em um quadro Excalidraw. Você não desenha elemento por elemento nem calcula posição: escreve um spec compacto (seções com a lista de caixas de um fluxo, pilhas de fichas e tabelas, e só no mapa e nos bastidores caixas posicionadas à mão) e o script `scripts/excalidraw_build.py` calcula layout, setas, legendas e a disposição em fileiras. O formato do spec está em `references/excalidraw-spec.md`; leia antes de escrever.

Como entregar:

1. Escreva o spec em `docs/walkthroughs/<slug>.spec.json` no repositório (crie a pasta se não existir). O spec fica versionado: é ele que permite ajustar o quadro depois sem recomeçar. Se já existe um spec para essa entrega, parta dele.
2. Rode `python <skill>/scripts/excalidraw_build.py docs/walkthroughs/<slug>.spec.json --out-dir docs/walkthroughs`. Saem `<slug>.excalidraw` e `<slug>.html` ao lado do spec.
3. Publique o `.html` com a Artifact tool (`file_path` = o html, `icon: "diagram"`, uma frase em `description`). É uma página comum, sem tipo de artifact; o Excalidraw vem de CDN e o quadro vai embutido. Se o spec já tem `artifact`, passe essa URL em `url` para atualizar o mesmo link; se não tem, grave a URL que a publicação devolveu no campo `artifact` do spec.
4. Mande o `.excalidraw` com SendUserFile (`display: attach`), para abrir no excalidraw.com, no VS Code ou no Obsidian.
5. Não verifique a página depois de publicar; se o usuário apontar algo torto, corrija o spec, rode o script de novo e republique.

Se a Artifact tool não existir na sessão, só o arquivo `.excalidraw` é entregue, e o chat diz onde ele está. Sem Python disponível, caia para a ferramenta de widget visual (`show_widget` do servidor visualize, com o `read_me` do módulo `diagram` antes), um widget por seção.

Regras dos diagramas, valem em qualquer ferramenta:

- 3 a 5 caixas por diagrama, título com o nome técnico e subtítulo explicativo de até 6 palavras, em fonte menor e cor mais apagada que o título. O diagrama de bastidores pode ter mais, desde que em camadas de no máximo 4 caixas lado a lado.
- Cores com significado fixo, sempre com legenda na própria seção: cinza = já existe e não muda; vermelho = onde está o problema hoje; verde = novo ou alterado; amarelo = decisão ou pendência; tracejado = acontece fora do fluxo ou depois.
- Fluxo de cima para baixo; mapa da arquitetura da esquerda para a direita.

## As seções do quadro

Uma seção (frame) por item abaixo, agrupadas em fileiras: **Fluxo** (antes, depois, bastidores), **Arquitetura** (mapa, peças tocadas), **Banco e performance** (banco, performance, frontend), **Decisões e riscos** (como chegou, riscos). Pule seções que não se aplicam (sem seção dizendo "não se aplica"), menos banco de dados, performance e riscos, que sempre existem.

Dentro de cada seção, o título fica no canto superior esquerdo e uma linha de contexto (no máximo duas) abaixo dele, em cor apagada. Todo o resto é caixa, seta, ficha ou tabela.

### Como chegou nessa implementação
Ficha com as decisões em que o conselho técnico pesou alternativas, no máximo cinco linhas: decisão, escolha, alternativa descartada, por quê. Cada célula em uma frase curta, linguagem de negócio. Se o conselho convergiu sem divergência nenhuma, a ficha tem uma linha dizendo isso.

### Mapa da arquitetura
Um diagrama só, mostrando quais sistemas e partes conversam entre si nessa entrega: sistemas externos (Shopify, Bling, Chatwoot...) como caixas soltas, o sistema que está sendo alterado como um contêiner tracejado com as peças envolvidas dentro. O que é novo fica em verde. Serve para o usuário se localizar antes de ver os fluxos.

Mostre só o que participa da mudança, não o sistema inteiro. Se a mudança vive dentro de uma única peça e não cruza fronteira nenhuma, pule esta seção.

### Antes e depois
Para cada fluxo cujo comportamento muda, duas seções lado a lado, de cima para baixo: como é hoje e como fica. Esta é a parte principal do quadro; o resto é apoio.

- Se a mudança é puramente aditiva (não havia fluxo antes), faça só o "depois" e diga isso na linha de contexto.
- Mais de um fluxo afetado: um par de seções por fluxo, no máximo três pares. Acima disso, agrupe.

### Bastidores
O mapa e o antes/depois resumem em uma caixa só tudo o que acontece depois que a pessoa já recebeu a resposta ("fila", "roda em segundo plano", "envia aos destinos"). Essa caixa é justamente a parte que o usuário não consegue imaginar sozinho, e ele não deveria precisar pedir para vê-la.

Faça a checagem: alguma seção anterior tem uma caixa que fala de fila, segundo plano, worker, job agendado, aviso recebido de outro sistema (webhook), nova tentativa ou envio para vários destinos? Se sim, abra essa caixa em uma seção própria, sem esperar pedido. A linha de contexto liga as duas: "A caixa 'fila' do Depois, por dentro, é assim."

O diagrama de bastidores mostra, de cima para baixo:

- **Quem dispara**: a peça que publica o trabalho e quantas mensagens saem (uma só, uma por destino...).
- **Por onde passa**: cada fila ou agendamento como uma caixa própria, com a garantia dela no subtítulo — se respeita ordem, quantas tentativas faz ("em ordem, até 8 tentativas", "sem ordem garantida").
- **Quem executa**: cada consumidor como uma caixa, com o que ele envia ou altera no subtítulo. Destinos diferentes ficam lado a lado.
- **Onde o resultado fica**: a caixa final que diz onde o sucesso ou a falha é registrado e como alguém fica sabendo.

As cores seguem a regra geral, e aqui elas respondem uma pergunta importante sem texto: a fila que já existe e está sendo reaproveitada fica cinza; o que é criado fica verde.

O caso de falha entra no próprio desenho: uma caixa vermelha ao lado do consumidor, "esgotou as tentativas", com seta para onde isso fica registrado e quem pode reenviar.

Se nada roda fora da espera da pessoa, pule a seção.

### Peças tocadas
Uma tabela só, backend e infraestrutura, com tudo o que muda ou nasce: colunas tipo, peça, o que ela faz hoje, o que muda. Uma linha por peça, sem listar arquivo por arquivo.

- **Tipo** é uma palavra: package, rota, fila, worker, job, webhook, tabela, lib, config, serviço externo. O que não existia recebe a célula de tipo em verde com "· NOVO" (`{"text": "rota · NOVO", "style": "green"}`), e a coluna "o que ela faz hoje" diz "não existia".
- Para o que nasce, "o que muda" responde para que serve: rota, quem chama e o que devolve; fila ou job, o que dispara e quando roda; lib instalada, o que faz e por que o que já existe não resolve; config ou serviço externo, o que precisa ser configurado e por quem.
- Se não há lib nova nem configuração sua, diga isso na linha de contexto ("Nenhum package novo é instalado").

### Banco de dados
Sempre presente, seção própria, nunca escondida em outra.

Sem migration: uma ficha só, "Sem migration: nada muda na estrutura do banco."

Com migration, uma ficha por migration, com quatro linhas nesta ordem:

- **O que muda**: tabela/coluna em linguagem de negócio, nome técnico depois.
- **Por quê**: qual parte do plano não funciona sem isso. Se dá para entender com um exemplo de dado, dê o exemplo.
- **Dados que já existem**: o que acontece com as linhas atuais (ficam vazias, são preenchidas por um script, nada).
- **Risco**: se é só adição (seguro, reversível) ou se altera/remove algo (pode travar tabela, perder dado, exigir ordem de deploy). Risco alto fica em vermelho.

### Performance
Sempre presente. O usuário quer sair sabendo se a entrega deixa algo mais rápido, mais lento ou igual, e se a solução escolhida aguenta o uso real.

Ficha-tabela com uma linha por fluxo afetado (e uma linha "resto do sistema" quando fizer sentido): fluxo, veredito, por quê.

- **Veredito** é uma destas palavras, como etiqueta colorida: melhora (verde), piora (vermelho), igual (cinza), ou novo (verde; diga se é leve ou pesado).
- **Por quê** aponta a causa concreta, em linguagem de quem usa: o que acontece na hora em que alguém espera a resposta e o que foi para segundo plano; consultas a mais ou a menos no banco; consulta repetida dentro de um laço; busca com ou sem índice; chamada a serviço externo no meio do caminho; cache; volume de dados carregado.

Abaixo da tabela, duas fichas pequenas:

- **O que faria ficar lento**: a condição em que a solução deixa de ser performática (volume, pico, limite de um serviço externo) e o que acontece nesse caso — atrasa, trava ou falha.
- **Custo novo**: recurso que passa a ser consumido (fila, memória, chamadas pagas a uma API), se houver.

Quando o veredito depende de algo ter ido para segundo plano, aponte para a seção de bastidores em vez de reexplicar o caminho.

Seja honesto sobre a origem do veredito. Sem medição, é uma estimativa a partir da leitura do código: escreva isso na linha de contexto em vez de inventar milissegundos. Se a implementação planejada tem um problema de performance evitável, diga qual é e qual seria a alternativa, e repita o ponto na seção de riscos.

### Frontend
Ficha com no máximo três linhas, só lógica e comportamento: o que a tela passa a fazer, de onde vem o dado, o que acontece no erro. Sem nomes de componente, hooks ou estilos, a não ser que o usuário pergunte.

### Riscos
Sempre presente. É o resultado da rodada de riscos do conselho técnico, consolidado por você; não é uma análise nova. A seção tem quatro blocos:

1. **Veredito**: ficha de duas frases: a arquitetura está certa ou não, e o tamanho do pior problema ("cria lixo em sistema externo, não perde dinheiro").
2. **O conselho discorda do plano**: só se houver. No máximo três fichas, numeradas, da mais importante à menos. Cada uma traz o problema, um cenário concreto de falha (com dado real se existir, como um pedido ou um valor) e a correção proposta. Diga se a correção mexe em módulo existente que outra pessoa mantém.
3. **Pontos de falha, por gravidade**: ficha-tabela que inclui também o que já está bem coberto, para o usuário ver o mapa inteiro de risco: ponto, gravidade, situação. Gravidade como etiqueta (Alta vermelha, Média amarela, Baixa cinza, Nula verde), sempre com o dano em poucas palavras ("Média: estoque errado"). Situação: "corrigível, entra no plano", "aceitável, já tem alarme X", "pendência: precisa de resposta de Fulano", ou, para divergência do conselho, a posição de cada agente em uma linha.
4. **O que resistiu**: as decisões que os agentes atacaram e ficaram de pé, cada uma com o porquê. Isso evita que a crítica seja lida como "refaz tudo".

Não invente problema para preencher a seção. Se o desenho resiste, diga isso claramente e liste só os pontos de falha residuais.

## O que vai no chat

Depois de publicar, a resposta no chat tem no máximo quatro linhas:

1. O link do quadro (e o caminho do `.excalidraw` no repositório).
2. A mudança técnica em uma frase.
3. Se houver, o ponto mais sério da seção de riscos em uma frase, apontando a seção.
4. Uma pergunta única e acionável: se quer que você leve as discordâncias do conselho para o plano e anote as pendências (quem precisa responder o quê) antes de implementar.

Nada de repetir no chat o que está desenhado. Se o usuário pedir detalhe de uma peça, aí sim responda em texto, e desça para arquivos, funções e código.

## Tom e tamanho

- Caixa: título de até 4 palavras mais o nome técnico, subtítulo de até 6. Ficha: cada célula uma frase. Se uma ficha está virando parágrafo, ela quer ser diagrama.
- Sem trechos de código, a não ser que o usuário peça. Assinatura de função e SQL não ajudam a entender a mudança.
- Não repita decisões de negócio que o planejamento já fechou; cite-as só quando explicam um porquê técnico.
- Se o quadro não cabe em doze seções, a entrega é grande demais para um walkthrough só: divida por fluxo e diga isso no chat.
