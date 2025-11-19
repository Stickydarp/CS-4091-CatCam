#!/usr/bin/env bash
# Simple dev container helper for CatCam — start/stop/exec
# Usage:
#   ./dev.sh up        # start container (detached)
#   ./dev.sh shell     # open interactive shell in container
#   ./dev.sh exec ...  # run arbitrary command inside container
#   ./dev.sh down      # stop and remove container

set -euo pipefail

COMPOSE_FILE="$(dirname "$0")/docker-compose.yml"
export COMPOSE_FILE

do_up() {
  docker compose -f "$COMPOSE_FILE" up -d --build
}

do_shell() {
  docker exec -it catcam-backend /bin/bash
}

do_exec() {
  shift
  if [ "$#" -eq 0 ]; then
    echo "usage: $0 exec <command>"
    exit 1
  fi
  ensure_running
  docker exec -it catcam-backend "$@"
}

ensure_running() {
  # check if container is running
  if [ -z "$(docker ps -q -f name=^/catcam-backend$)" ]; then
    echo "Container 'catcam-backend' is not running. Start it with: $0 up"
    exit 1
  fi
}

do_demo() {
  ensure_running
  docker exec -it catcam-backend python -m scripts.demo_commands
}

do_test() {
  ensure_running
  docker exec -it catcam-backend python -m scripts.test_commands
}

do_init_db() {
  ensure_running
  docker exec -it catcam-backend python -m catCamBackend.main init_db
}

do_list() {
  ensure_running
  docker exec -it catcam-backend python -m catCamBackend.main list
}

do_classify_all() {
  ensure_running
  docker exec -it catcam-backend python -m catCamBackend.main classify_all
}

do_insert() {
  ensure_running
  if [ -z "${2:-}" ]; then
    echo "usage: $0 insert <filename>"
    exit 1
  fi
  # $2 is the filename
  docker exec -it catcam-backend python -m catCamBackend.main insert_metadata --filename "$2"
}

do_down() {
  docker compose -f "$COMPOSE_FILE" down
}

case "${1:-}" in
  up) do_up ;; 
  shell) do_shell ;; 
  exec) do_exec "$@" ;; 
  demo) do_demo ;; 
  test) do_test ;; 
  init_db) do_init_db ;; 
  list) do_list ;; 
  classify_all) do_classify_all ;; 
  insert) do_insert "$@" ;; 
  down) do_down ;; 
  *)
    echo "Usage: $0 {up|shell|exec|demo|test|init_db|list|classify_all|insert|down}"
    exit 2
    ;;
esac
