# Velozo Skills

Skills que eu uso no dia a dia com agentes de código (Claude Code, Codex e afins), direto do meu diretório de skills.

Elas são pequenas, fáceis de adaptar e combinam com as [skills do Matt Pocock](https://github.com/mattpocock/skills): planejo com `/grill-me` ou `/grill-with-docs` e, com a decisão de negócio fechada, uso as skills daqui para enxergar o lado técnico antes de implementar. Mexa nelas e adapte ao seu jeito.

## Instalação

Um plugin se atualiza sozinho. O [skills.sh](https://skills.sh/bielvelozo/velozo-skills) copia arquivos editáveis para o seu projeto, e você atualiza na mão. Escolha um por agente; instalar os dois dá cada skill em dobro.

### 1. Pegue as skills

<details>
<summary><strong>Claude Code</strong></summary>

```bash
claude plugin marketplace add bielvelozo/velozo-skills
```

```bash
claude plugin install velozo-skills@velozo
```

Atualiza sozinho.

</details>

<details>
<summary><strong>Codex</strong></summary>

```bash
codex plugin marketplace add bielvelozo/velozo-skills
```

```bash
codex plugin add velozo-skills@velozo
```

Atualiza ao iniciar.

</details>

<details>
<summary><strong>Qualquer outro agente, ou arquivos editáveis</strong> (atualização manual)</summary>

```bash
npx skills@latest add bielvelozo/velozo-skills -a <agent>  # cursor, opencode, windsurf, amp; sem -a para escolher
```

Para atualizar, `npx skills@latest update`.

</details>

<details>
<summary><strong>Clonando o repositório</strong> (para quem quer editar as skills)</summary>

```bash
git clone https://github.com/bielvelozo/velozo-skills.git && cd velozo-skills && scripts/link-skills.sh
```

Cria um link simbólico de cada skill em `~/.claude/skills` e `~/.agents/skills`; um `git pull` atualiza tudo.

</details>

### 2. Pré-requisitos

- **Python 3** no PATH: a `tech-walkthrough` gera o quadro Excalidraw com um script.
- Claude Code com a ferramenta **Artifact** (para publicar o quadro com link). Sem ela, a skill entrega só o arquivo `.excalidraw`.

### 3. Pronto.

## Por que essas skills existem

### O plano ficou claro, a implementação não

**O problema.** Uma sessão de `/grill-me` deixa as decisões de negócio bem definidas. Mas a parte técnica (qual rota nasce, qual fila é reaproveitada, se tem migration e por quê, o que roda em segundo plano) fica espalhada em parágrafos, e eu não tenho o código inteiro na cabeça para acompanhar.

**A solução.** Um quadro Excalidraw, um campo só, com o antes e o depois de cada fluxo, o mapa dos sistemas que conversam, os bastidores (filas, workers, retentativas), a migration com o porquê, o veredito de performance e os riscos que sobram. Cada peça do código é apresentada pelo que ela faz, e o nome técnico vem depois. A implementação explicada sai de um debate entre três agentes (mínimo, robusto, performance), e não da primeira ideia que funciona.

É o `/tech-walkthrough`.

## Referência

As skills se dividem por quem pode invocar. **User-invoked** só rodam quando você digita o nome delas. **Model-invoked** podem ser digitadas ou acionadas pelo agente quando a tarefa encaixa.

### Engineering

Skills para o trabalho com código.

#### Model-invoked

- **[tech-walkthrough](./skills/engineering/tech-walkthrough/SKILL.md)**: Explica a parte técnica de um plano já decidido num quadro Excalidraw: antes e depois, mapa da arquitetura, bastidores, migrations, performance e riscos. Três agentes debatem a melhor implementação antes de desenhar. `fast` pula o debate.

## Licença

MIT.
