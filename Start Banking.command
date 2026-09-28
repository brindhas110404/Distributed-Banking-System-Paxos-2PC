#!/bin/bash
set -e
cd "$(dirname "$0")"
if [ ! -x bin/banking ]; then
  ./Rebuild.command
fi
echo "For the included test cases, enter 3 clusters and 3 servers per cluster."
echo "Press Control-C to stop."
exec ./bin/banking
