#!/usr/bin/env bash

ORIG_DIR="$(pwd)"
cd "$(dirname "$0")"
BIN_DIR="$(pwd)"

onExit() {
  cd "${ORIG_DIR}"
}

trap onExit EXIT

helm template --values login-service-values.yaml um-login-service login-service
# helm upgrade -i --values login-service-values.yaml um-login-service login-service
