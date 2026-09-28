#!/bin/bash
set -e
cd "$(dirname "$0")"
if [ -x .tools/go/bin/go ]; then
  GO_BIN="$PWD/.tools/go/bin/go"
else
  GO_BIN="$(command -v go || true)"
fi
if [ -z "$GO_BIN" ]; then
  echo "Install Go 1.23.2 or later from https://go.dev/dl/ and try again."
  exit 1
fi
export GOPATH="$PWD/.tools/gopath"
export GOCACHE="$PWD/.tools/cache"
export CGO_ENABLED=1
"$GO_BIN" build -o bin/banking .
echo "Build complete. Open Start Banking.command to run."
