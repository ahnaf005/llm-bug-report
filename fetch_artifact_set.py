import os
import json
import random
from typing import List

from bugswarm.common.rest_api.database_api import DatabaseAPI

# ---------------------------
# CONFIG
# ---------------------------

# Number of artifacts you want
NUM_ARTIFACTS = 40

# Approximate max tokens allowed for (build log + code diff)
# Rough heuristic: ~4 characters per token
MAX_TOKENS = 200_000

# Output file
OUTPUT_FILE = "java_artifacts_40.txt"

# BugSwarm API token (or read from env)
BUGSWARM_TOKEN = os.getenv("BUGSWARM_TOKEN", "ECS245-TOKEN")  # replace if needed


# ---------------------------
# Helper functions
# ---------------------------

def approx_token_count(text: str) -> int:
    """
    Very rough token approximation: ~4 characters per token.
    This is enough for filtering large logs.
    """
    return len(text) // 4


def get_java_artifacts(api: DatabaseAPI) -> List[dict]:
    """
    Return metadata for Java artifacts that have at least one reproduce success.
    Uses BugSwarm filter_artifacts with a Mongo-like query.
    """
    api_filter = '{"reproduce_successes":{"$gt":0}, "lang":"Java"}'
    print("Fetching Java artifacts from BugSwarm...")
    artifacts = api.filter_artifacts(api_filter)
    print(f"Found {len(artifacts)} Java artifacts with reproduce_successes > 0.")
    return artifacts


# ---------------------------
# Main logic
# ---------------------------

def main():
    api = DatabaseAPI(token=BUGSWARM_TOKEN)

    all_java_artifacts = get_java_artifacts(api)
    if not all_java_artifacts:
        print("No artifacts returned from BugSwarm. Exiting.")
        return

    # Shuffle to get random artifacts
    random.shuffle(all_java_artifacts)

    selected_tags: List[str] = []

    for artifact in all_java_artifacts:
        if len(selected_tags) >= NUM_ARTIFACTS:
            break

        image_tag = artifact.get("image_tag")
        if not image_tag:
            continue

        print(f"\nChecking artifact: {image_tag}")

        # Get diff
        try:
            code_diff = api.get_diff(image_tag)
        except Exception as e:
            print(f"  Skipping {image_tag}: error getting diff ({e})")
            continue

        if not code_diff:
            print(f"  Skipping {image_tag}: empty or missing diff.")
            continue

        # Get failing job build log
        failed_job = artifact.get("failed_job", {})
        job_id = failed_job.get("job_id")
        if not job_id:
            print(f"  Skipping {image_tag}: missing failed_job.job_id.")
            continue

        try:
            build_log = api.get_build_log(str(job_id))
        except Exception as e:
            print(f"  Skipping {image_tag}: error getting build log ({e})")
            continue

        if not build_log:
            print(f"  Skipping {image_tag}: empty build log.")
            continue

        # Combine build log + diff as text
        merged_text = f"""
========================
BUILD LOG
========================
{build_log}

========================
CODE DIFF
========================
{json.dumps(code_diff, indent=2)}
"""

        token_estimate = approx_token_count(merged_text)
        print(f"  Approx. tokens: {token_estimate}")

        if token_estimate <= MAX_TOKENS:
            print(f"  ✔ Accepted {image_tag}")
            selected_tags.append(image_tag)
        else:
            print(f"  ✘ Rejected {image_tag}: exceeds {MAX_TOKENS} tokens.")

    # Save results
    if not selected_tags:
        print("No artifacts satisfied the token limit. Nothing to write.")
        return

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for tag in selected_tags:
            f.write(tag + "\n")

    print("\nDone.")
    print(f"Selected {len(selected_tags)} artifact image tags.")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
