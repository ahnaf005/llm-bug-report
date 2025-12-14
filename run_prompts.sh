#!/bin/bash

# Check if an argument is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <artifact-name>"
    exit 1
fi

ARTIFACT_NAME=$1

# # Run Python scripts in sequence
# python gemini_api_simple_prompt.py "$ARTIFACT_NAME"
# python gemini_api_smart_prompt.py "$ARTIFACT_NAME"
# python openai_api_simple_prompt.py "$ARTIFACT_NAME"
# python openai_api_smart_prompt.py "$ARTIFACT_NAME"
# python test_descriptive.py "$ARTIFACT_NAME"

# Run Python scripts in sequence
python3 gemini_api_simple_prompt.py "$ARTIFACT_NAME"
python3 gemini_api_smart_prompt.py "$ARTIFACT_NAME"
python3 openai_api_simple_prompt.py "$ARTIFACT_NAME"
python3 openai_api_smart_prompt.py "$ARTIFACT_NAME"
python3 test_descriptive.py "$ARTIFACT_NAME"
