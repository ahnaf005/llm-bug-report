import sys
import os
import spacy
import textdescriptives as td
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="textdescriptives.components.coherence")


def compute_readability(file_path, nlp):
    if not os.path.exists(file_path):
        print(f"[WARN] File not found: {file_path}")
        return None
    
    with open(file_path, "r") as f:
        text = f.read()

    doc = nlp(text)
    return doc._.readability.get("flesch_reading_ease")


def main():
    # -------------------------
    # Check CLI argument
    # -------------------------
    if len(sys.argv) < 2:
        print("Usage: python script.py <artifact-name>")
        return

    artifact = sys.argv[1]
    base = f"output/{artifact}"

    # -------------------------
    # File paths
    # -------------------------
    files = {
        "gemini_simple": f"{base}/gemini_api/simple_report_{artifact}.txt",
        "gemini_smart":  f"{base}/gemini_api/smart_report_{artifact}.txt",
        "openai_simple": f"{base}/openai_api/simple_report_{artifact}.txt",
        "openai_smart":  f"{base}/openai_api/smart_report_{artifact}.txt",
    }

    # -------------------------
    # Load spaCy + TextDescriptives
    # -------------------------
    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe("textdescriptives/all")

    # -------------------------
    # Compute readability
    # -------------------------
    results = {}

    for name, path in files.items():
        print(f"\nProcessing {name}: {path}")
        score = compute_readability(path, nlp)
        results[name] = score
        print(f"  → flesch_reading_ease = {score}")

    # -------------------------
    # Save results to file
    # -------------------------
    out_path = f"{base}/readibility_report.txt"
    with open(out_path, "w") as f:
        for name, score in results.items():
            f.write(f"{name}: {score}\n")

    print(f"\nSaved readability report to: {out_path}")


if __name__ == "__main__":
    main()
