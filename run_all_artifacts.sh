#!/bin/bash

# Usage:
#   ./run_all_artifacts.sh <artifact-name>
#   ./run_all_artifacts.sh <artifacts-file>   # java_artifacts_40.txt

if [ $# -ne 1 ]; then
    echo "Usage: $0 <artifact-name | artifacts-file>"
    exit 1
fi

INPUT=$1

run_for_artifact() {
    local ARTIFACT_NAME="$1"

    echo "====================================="
    echo "Processing artifact: $ARTIFACT_NAME"
    echo "====================================="

    python3 gemini_api_simple_prompt.py "$ARTIFACT_NAME"
    python3 gemini_api_smart_prompt.py "$ARTIFACT_NAME"
    python3 openai_api_simple_prompt.py "$ARTIFACT_NAME"
    python3 openai_api_smart_prompt.py "$ARTIFACT_NAME"
    python3 test_descriptive.py "$ARTIFACT_NAME"
}

# If INPUT is a file, treat it as a list of artifacts; otherwise treat it as a single artifact name
if [ -f "$INPUT" ]; then
    while IFS= read -r ARTIFACT_NAME; do
        # skip empty lines
        [ -z "$ARTIFACT_NAME" ] && continue
        run_for_artifact "$ARTIFACT_NAME"
    done < "$INPUT"
else
    run_for_artifact "$INPUT"
fi
