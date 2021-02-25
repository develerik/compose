#!/usr/bin/env sh
#
# docker-compose wrapper for easy management.

display_help() {
  basename=$(basename "$0")

  printf 'docker-compose wrapper for easy management.

Usage:
  %s ls [--long]
  %s stack [DOCKER-COMPOSE COMMAND]
  %s [--create|--remove] stack
  %s --help

Options:
  --create\tCreate a new stack
  --remove\tRemove the stack  

Commands:
  ls\t\tList all available stacks\n' "$basename" "$basename" "$basename" "$basename"
}

case "$1" in
  "ls")
    echo "Not yet implemented"
    exit 1
    ;;
  "--create")
    echo "Not yet implemented"
    exit 1
    ;;
  "--remove")
    echo "Not yet implemented"
    exit 1
    ;;
  "--help")
    display_help
    exit 1
    ;;
esac
