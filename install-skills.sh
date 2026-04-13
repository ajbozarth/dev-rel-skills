#!/usr/bin/env bash
# Creates symlinks in ~/.claude/skills/ for each skill directory in skills/

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_SRC="$SCRIPT_DIR/skills"
SKILLS_DST="$HOME/.claude/skills"

mkdir -p "$SKILLS_DST"

for dir in "$SKILLS_SRC"/*/; do
  name="$(basename "$dir")"
  target="$SKILLS_DST/$name"
  if [ -L "$target" ]; then
    echo "updating: $name"
    rm "$target"
  elif [ -e "$target" ]; then
    echo "skipping: $name (non-symlink already exists)"
    continue
  else
    echo "linking:  $name"
  fi
  ln -s "$dir" "$target"
done
