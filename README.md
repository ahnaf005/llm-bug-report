# Evaluating LLM-Generated Bug Reports Using CI Failures and Code Diffs

This project investigates how effectively modern Large Language Models (LLMs), including OpenAI and Google Gemini variants, can generate high-quality bug reports from real-world software artifacts in the [BugSwarm](http://www.bugswarm.org) dataset, a large-scale collection of reproducible CI (Continuous Integration) failures. For each failing artifact from BugSwarm, we extract build logs and code diffs (code difference before and after applying the patch), input them to LLMs, apply two prompting strategies (“simple” and “smart”), and evaluate the generated reports using a custom rubric that measures correctness, completeness, clarity, and technical accuracy.

## 1. Selecting a set of artifacts

Running the script in [fetch_artifact_set.py](fetch_artifact_set.py) will generate a list of artifact names. Those names are randomly selected from the list of all artifacts from BugSwarm. The size of the list can be adjusted by changing the `NUM_ARTIFACTS`variable in the script. The `MAX_TOKENS` variable limits the script to select an artifact that has tokens (build log + code diffs) under a threshold. Also, the script is only selecting artifact that uses Java, as the build logs between Java and Python artifacts are very different.

[data/java_artifacts_40.txt](./data/java_artifacts_40.txt) already contains 40 randomly selected artifact names.

## 2. Set up and Generate Bug Reports

Install Docker: <https://docs.docker.com/engine/install>

### 2.1. Models and Prompts

Using Google's `gemini-2.5-flash` and OpenAI's `gpt-5-mini` as LLMs. For each model, we generate one bug report using "simple" prompt and one using "smart" prompt. Thus, from one artifact, we can generate 4 bug reports.

### 2.2. Set up and Generate

#### There are two options to run the projects.

#### Without using Docker(Set up dependencies in a local/virtual environment)

Clone the repository

Install the dependencies:

Install the BugSwarm toolset and the client with `pip` (requires Python 3.8 or later):
```
python3 -m pip install bugswarm-common bugswarm-client
```
Install google.generativeai for Gemini:  
```
pip3 install google.generativeai
```
  
Install openai for OpenAI: 
```
pip3 install openai
```
  
Install the readability tool, we use `textdescriptives` to automatically generate a readability score for the bug report:
```
pip3 install spacy textdescriptives
python -m spacy download en_core_web_sm
```

#### Using Docker

To run the project environment in Docker:`
```
docker build -t llm-bug-report
docker run -it  llm-bug-report
```
To run the project environment in Docker with a sandbox(Can be used to copy/move files between local and docker environment):
```
mkdir ~/llm-sandbox
docker run -it -v ~/llm-sandbox:/sandbox llm-bug-report
```
To run the project without building and directly from DockerHub:
```
docker pull ahnaf005/llm-bug-report:latest
docker run -it ahnaf005/llm-bug-report
```
After running either of these options, you can see the command line interface (CLI) inside the project(app) directory and follow the next section to actually generate bug reports. If there are any permission-related issues, try using `sudo` before the `docker` commands. Inside the docker environment, commands like `less` and `vim` can be used to view the reports.

#### To generate the bug report

After the dependencies are set up in the environment or running the docker, set up the LLM API key in the environment:
```
export OPENAI_API_KEY="YOUR_KEY"
export GEMINIAI_API_KEY="YOUR_KEY"
```
To generate the bug reports and readability scores for ONE artifact (approx. 1 - 3 mins, varies depending on the size of the build log + code diff, the max we experienced is around 3 mins)
```
./run_prompts.sh <ARTIFACT_TAG>
```
This will generate all 4 reports and their readability scores, and they will be saved to the output folder named by the corresponding artifact. We generate reports for one artifact each time due to the LLM API usage limitations.

To run all artifacts in `java_artifacts_40.txt` and generate reports for all of them (Not recommended, this might take more than two hours):
```
./run_all_artifacts.sh java_artifacts_40.txt
```
If there is any permission related issues, try running the following
```
chmod +x 'executable-file-name'
```

The [output](./output) folder contains LLM-generated bug reports and their readability scores for over 40 artifact.

## 3. Evaluation

### 3.1. Custom rubric
To evaluate the quality of the generated reports, we create a custom rubric:

- Key-Aspect Completeness (Total score: 4):
    - Triggering information (Score: 0 / 1): Includes the relevant methods and the triggering conditions or parameters.
    - Expected behavior(Score: 0 / 1): Describes the intended behavior of the program.
    - Observed behavior(Score: 0 / 1): Describes the actual behavior of the program.
    - Steps to reproduce(Score: 0 / 1): Lists the procedures needed to trigger the bug.

- Code samples (Score: 0 / 0.5 / 1). We examined whether the bug report includes the relevant code snippet where the bug occurs

- Stack Traces (Score: 0 / 0.5 / 1). A complete and focused stack trace that includes all essential lines necessary for debugging.

- Patches (Score: 0 / 1). A description of a patch or fix.

- Readability (Score: 0 / 0.5 / 1 / 1.5 / 2). Using the scores from the readability tool and normalising those scores based on all the readability tools, so each normalising score will get 0, 0,5, 1, 1.5, or 2.

- Structure (Score: 0 / 1). This metric evaluates the overall organisation of the report

### 3.2. Statistics Analysis

We manually scored all the reports using the custom rubric and computed a statistical analysis on the scores of the bug reports.

Here are the results of the statistical analysis:
![Screenshot](./image/table1.png)

All the scoring can be found [here](./data/Bug_Report_Manuel_Evaluation_Scores.csv). 

