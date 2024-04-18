#!/bin/bash

set -e

# output is the first argument, the rest are the inputs
OUT=$1
shift
echo "tar czf $OUT $@"
tar czf $OUT "$@"


