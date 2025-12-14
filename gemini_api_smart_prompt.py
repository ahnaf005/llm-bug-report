import sys
import os
import json
from bugswarm.common.rest_api.database_api import DatabaseAPI
import google.generativeai as genai


def main():
    # -----------------------------
    # 1. Check for command argument
    # -----------------------------
    if len(sys.argv) < 2:
        print("Usage: python example.py <artifact-name>")
        return

    artifact_name = sys.argv[1]
    api = DatabaseAPI(token='ECS245-TOKEN')

    # ------------------------------------
    # 2. Validate artifact name via diff
    # ------------------------------------
    code_diff = api.get_diff(artifact_name)
    if code_diff is None or code_diff == {}:
        print(f"Error: Artifact '{artifact_name}' not found or diff unavailable.")
        return

    # ------------------------------------
    # 3. Get artifact metadata
    # ------------------------------------
    artifact_resp = api.find_artifact(artifact_name)
    if not artifact_resp or artifact_resp.status_code != 200:
        print(f"Error: Could not get artifact info for '{artifact_name}'")
        return

    artifact = artifact_resp.json()
    job_id = artifact["failed_job"]["job_id"]

    # ------------------------------------
    # 4. Get build log
    # ------------------------------------
    failed_build_log = api.get_build_log(str(job_id))
    if failed_build_log is None:
        print("Error: Could not retrieve build log.")
        return

    # ------------------------------------
    # 5. Create output directory
    # ------------------------------------
    out_dir = f"output/{artifact_name}"
    os.makedirs(out_dir, exist_ok=True)

    # ------------------------------------
    # 6. Merge BUILD LOG + CODE DIFF in one file
    # ------------------------------------
    merged_path = os.path.join(out_dir, f"merged_input_{artifact_name}.txt")

    merged_text = f"""
========================
BUILD LOG
========================
{failed_build_log}

========================
CODE DIFF
========================
{json.dumps(code_diff, indent=2)}
"""

    with open(merged_path, "w", encoding="utf-8") as f:
        f.write(merged_text)

    print(f"✔ Merged build log + diff → {merged_path}")

    # ------------------------------------
    # 7. Generate bug report via Gemini (file upload)
    # ------------------------------------

    print("Uploading merged file to Gemini API...")

    genai.configure(api_key = os.getenv("GEMINIAI_API_KEY"))  #export GEMINIAI_API_KEY="Your Key"
    model = genai.GenerativeModel("gemini-2.5-flash")

    uploaded_file = genai.upload_file(path=merged_path)
    print("✔ File uploaded. Asking LLM for bug report...")

    prompt = """
    The uploaded file contains TWO sections:
    1. BUILD LOG
    2. CODE DIFF

    Both are required for full debugging context.

    You are a software engineer assistant. Based on the build log and code diff, generate a detailed bug report that includes:
    1. Title: Provide a concise title describing the bug.
    2. Steps to Reproduce: List clear, itemized steps.
    3. Triggering Input: Include the input, parameters, or conditions that caused the bug.
    4. Expected Behavior: Describe what the program should do.
    5. Observed Behavior: Describe what actually happens, including error messages.
    6. Relevant Code Snippets: Include relevant code from the diff.
    7. Stack Traces: Include necessary stack trace from the build log.
    8. Patches / Suggested Fixes: Include if available in the diff.
    """

    response = model.generate_content(
    [prompt, uploaded_file],
    generation_config={
        "temperature": 0,
        "top_p": 1,
        "top_k": 1,
    }
    )

    bug_report = response.text

    # Save bug report under out_dir/gemini_api/
    gemini_dir = os.path.join(out_dir, "gemini_api")
    os.makedirs(gemini_dir, exist_ok=True)

    bug_report_path = os.path.join(gemini_dir, f"smart_report_{artifact_name}.txt")

    with open(bug_report_path, "w", encoding="utf-8") as f:
        f.write(bug_report)

    print(f"✔ Bug report saved to {bug_report_path}")
    print("Done.")



if __name__ == "__main__":
    main()
