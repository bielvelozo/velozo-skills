---
name: map
description: Desenha, atualiza ou consulta o mapa do projeto (HTML em .project-map/) com as partes, o andamento de cada uma, o que está travado e o próximo passo, usando o subagente project-map. Use só quando o usuário pedir — "/map", "desenha o mapa", "atualiza o mapa", "onde estamos?".
---

# Mapa do projeto

O mapa é desenhado pelo subagente `project-map`. Esta skill prepara o pedido, dispara o subagente e resume o resultado.

## Passos

1. **Estilo.** Leia `~/.claude/agent-memory/project-map/MEMORY.md`. Se ainda não tiver tema e cor de destaque, pergunte ao usuário (claro ou escuro; uma cor de destaque) e grave a resposta nesse arquivo antes de seguir. O subagente não pode fazer perguntas.

2. **`.gitignore`.** Se o projeto for repositório git, garanta que `.project-map/` está no `.gitignore` da raiz. Não faça commit só por isso.

3. **"Onde estamos?"** Se o usuário só quer saber o estado e `.project-map/estado.json` existe, responda a partir dele, dizendo a data do mapa. Se houver commits depois do último commit registrado no mapa, ofereça atualizar. Pare aqui.

4. **Desenhar ou atualizar.** Chame o Agent com `subagent_type: project-map`, em segundo plano. No pedido, inclua:
   - a raiz do projeto;
   - o que foi feito desde o último mapa (resumo desta sessão);
   - marcos que o usuário já definiu, se houver;
   - decisões pendentes com o padrão sugerido para cada uma.

   Continue o trabalho enquanto ele roda.

5. **Resumo.** Quando ele terminar, diga em poucas linhas o próximo marco, o próximo passo, o que mudou e as decisões pendentes, com o link para `.project-map/index.html`.
