#!/usr/bin/env bash
set -euo pipefail

# Liga toda skill do repositório (fora de deprecated/) nos diretórios locais de
# skills de cada agente:
#   - ~/.claude/skills: Claude Code
#   - ~/.agents/skills: Codex e outros compatíveis com Agent Skills
# Cada entrada é um link simbólico para este repositório, então um `git pull`
# basta para atualizar. No Windows (Git Bash), rode com
# MSYS=winsymlinks:nativestrict e o modo de desenvolvedor ligado, senão o `ln`
# copia em vez de linkar.

REPO="$(cd "$(dirname "$0")/.." && pwd)"
DESTS=("$HOME/.claude/skills" "$HOME/.agents/skills")

names=()
srcs=()
while IFS= read -r -d '' skill_md; do
  src="$(dirname "$skill_md")"
  names+=("$(basename "$src")")
  srcs+=("$src")
done < <(find "$REPO/skills" -name SKILL.md -not -path '*/node_modules/*' -not -path '*/deprecated/*' -print0)

for DEST in "${DESTS[@]}"; do
  if [ -L "$DEST" ]; then
    resolved="$(readlink -f "$DEST")"
    case "$resolved" in
      "$REPO"|"$REPO"/*)
        echo "erro: $DEST é um link para dentro deste repositório ($resolved)." >&2
        echo "Remova (rm \"$DEST\") e rode de novo; o script recria como pasta de verdade." >&2
        exit 1
        ;;
    esac
  fi

  mkdir -p "$DEST"

  for i in "${!names[@]}"; do
    name="${names[$i]}"
    src="${srcs[$i]}"
    target="$DEST/$name"

    if [ -e "$target" ] && [ ! -L "$target" ]; then
      rm -rf "$target"
    fi

    ln -sfn "$src" "$target"
    echo "linked $name -> $src ($DEST)"
  done
done
