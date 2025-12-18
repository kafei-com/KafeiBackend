#!/bin/bash
set -e
TARGET="output_$(date +%s)"
mkdir -p $TARGET
echo "Scaffold files" > $TARGET/README.md
zip -r project.zip $TARGET
echo "ZIP ready"
