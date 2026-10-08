## O que faz

`tech-walkthrough` pega um plano já decidido no negócio e mostra **o que vai acontecer no código**, num quadro Excalidraw só: o antes e o depois de cada fluxo, o mapa dos sistemas que conversam, os bastidores (fila, worker, retentativa, onde o resultado fica), a migration com o porquê, o veredito de performance e os riscos que sobram. O chat recebe o link e três linhas; o resto é desenho.

Ela não explica a implementação que você teria escrito de primeira. Antes de desenhar, três agentes com vieses diferentes (mínimo, robusto, performance) propõem, criticam e convergem para a implementação, e o quadro explica a que saiu do debate, com as alternativas descartadas e os pontos de falha que cada um encontrou.

Toda peça do código aparece pelo que ela faz, e o nome técnico vem depois ("no package que mantém a cópia local dos pedidos, `packages/mirror`"). A skill parte do princípio de que você não tem o código inteiro na cabeça.

## Quando usar

Digite `/tech-walkthrough`, ou o agente aciona sozinho quando você pede para entender a parte técnica, pergunta se tem migration ou se algo vai ficar lento.

Use **depois** de um planejamento (`/grill-me`, `/grill-with-docs`, um spec, uma issue) e **antes** de implementar. Se o plano de negócio ainda está aberto, é cedo: volte para o grilling. Se o que você quer é a lista de tarefas, não o entendimento, use [to-tickets](https://github.com/mattpocock/skills/blob/main/skills/engineering/to-tickets/SKILL.md).

| Situação | O que fazer |
|---|---|
| Entrega com decisão técnica em aberto (fila nova ou reaproveitada, tabela ou campo livre, lib ou código próprio) | `/tech-walkthrough`: o conselho decide |
| Entrega pequena, sem decisão em aberto (uma rota, um campo) | `/tech-walkthrough fast`: sem debate, você decide, riscos numa passada só |
| Entrega grande demais para um quadro (mais de três fluxos mudando) | Divida por fluxo e rode uma vez por fluxo |

## Pré-requisitos

- Python 3 no PATH: o quadro é gerado por `scripts/excalidraw_build.py` a partir de um spec.
- Um repositório aberto: o spec e o `.excalidraw` ficam em `docs/walkthroughs/` para o quadro poder ser ajustado depois.
- A ferramenta Artifact do Claude Code, para publicar o quadro com link. Sem ela, a skill entrega só o arquivo `.excalidraw`, que abre no excalidraw.com, no VS Code ou no Obsidian.

## O conselho técnico

A escolha da implementação passa por um debate em rodadas: cada agente propõe pelo seu viés lendo o código, recebe as propostas dos outros dois e responde o que aceita e o que mantém (objeção só vale com fato do código ou cenário concreto), e por fim lista o que ainda pode quebrar na implementação fechada. O orquestrador consolida: fato vence opinião, empate de gosto vai para o mínimo, e o que o plano já decidiu não se reabre em silêncio.

O debate não aparece no quadro. O que aparece é o resultado: a seção **Como chegou nessa implementação** (decisão, escolha, descartada, por quê) e a seção **Riscos** (veredito, onde o conselho discorda do plano, pontos de falha por gravidade, o que resistiu).

## Os bastidores

A caixa "fila" de um fluxo esconde justamente a parte que você não consegue imaginar sozinho: quem publica e quantas mensagens, por qual fila e com que garantia (ordem, tentativas), quem consome, onde o resultado fica, o que acontece quando as tentativas acabam. A skill abre essa caixa numa seção própria sempre que um diagrama anterior menciona fila, worker, job, webhook ou retentativa, sem esperar você pedir.

## Perguntas comuns

**Por que Excalidraw e não texto?**
Porque o problema que a skill resolve é de leitura, não de informação: o conteúdo técnico já estava nos parágrafos do plano, e mesmo assim não dava para enxergar o que mudava. Caixa, seta e cor com significado fixo (cinza já existe, vermelho é o problema, verde é novo, tracejado acontece depois) carregam isso em segundos.

**Posso editar o quadro?**
Sim. A página publicada é o Excalidraw de verdade, e o `.excalidraw` abre em qualquer editor compatível. Para mudar o conteúdo e manter o link, edite o spec em `docs/walkthroughs/` e rode a skill de novo; ela republica no mesmo artifact.

**O conselho demora. Vale a pena sempre?**
Não. Ele existe para decisão técnica em aberto. Para uma entrega pequena, `fast` pula o debate e custa uma passada só.

**A seção de riscos é uma auto-análise separada?**
Não. É a última rodada do mesmo debate, consolidada: os pontos de gravidade alta são conferidos no código pelo orquestrador antes de entrar no quadro.

## Está funcionando se

- Você entende o que muda olhando o antes e o depois, sem ler a tabela.
- Cada caixa tem o nome real que você vai achar no código ou no console (fila, worker, rota), não um nome inventado.
- A seção de bastidores apareceu sem você pedir, sempre que havia fila ou job no caminho.
- A migration tem um porquê que você consegue repetir para outra pessoa.
- O chat tem quatro linhas, e o resto está no quadro.

## Onde se encaixa

É um passo de corrente: `grill-me` ou `grill-with-docs` → **tech-walkthrough** → `to-tickets` ou `implement`. Entra quando o negócio está decidido e sai com a implementação escolhida e desenhada; os itens em que o conselho discorda do plano voltam para o plano antes de virar ticket.
