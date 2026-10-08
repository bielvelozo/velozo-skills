As skills ficam em pastas de bucket dentro de `skills/`:

- `engineering/`: trabalho com código, uso diário
- `productivity/`: fluxo de trabalho sem código, uso diário
- `in-progress/`: beta, pública de propósito, não entra no plugin
- `deprecated/`: não usa mais

Toda skill em `engineering/` ou `productivity/` (os buckets **promovidos**) precisa de uma entrada no `README.md` da raiz e de uma entrada no array `skills` de `.claude-plugin/plugin.json` (o plugin do Claude Code entrega exatamente o conjunto promovido). Skills em `in-progress/` e `deprecated/` não aparecem em nenhum dos dois.

Cada pasta de bucket tem um `README.md` que lista toda skill do bucket com uma descrição de uma linha, o nome ligado ao `SKILL.md`. Os buckets promovidos e o `README.md` da raiz agrupam em **User-invoked** e **Model-invoked**; os outros usam lista simples.

Cada skill promovida tem também uma página de docs em `docs/<bucket>/<skill>.md`, com as seções **O que faz**, **Quando usar**, **Perguntas comuns** e **Está funcionando se**. Quando uma skill promovida é criada, renomeada ou muda de comportamento, crie ou ressincronize a página.

Cada `SKILL.md` é user-invoked (`disable-model-invocation: true` no frontmatter e `policy.allow_implicit_invocation: false` em `agents/openai.yaml`) ou model-invoked (descrição com gatilhos ricos e `allow_implicit_invocation: true`).

`.claude-plugin/marketplace.json` é o marketplace do próprio repositório. Depois de mexer em qualquer manifesto, rode `claude plugin validate . --strict`.

Para (re)ligar toda skill fora de `deprecated/` nos diretórios locais de skills (`~/.claude/skills`, `~/.agents/skills`), rode `scripts/link-skills.sh`. Cada entrada é um link simbólico para este repositório; rode de novo depois de criar, remover ou renomear uma skill.

Argumentos de skill (`fast`, por exemplo) e nomes de arquivo são em inglês. O texto das skills e dos docs é em português.
