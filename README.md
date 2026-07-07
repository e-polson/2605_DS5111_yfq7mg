# DS-5111 VM Setup Guide & Infrastructure Runbook

This repository contains the automation scripts, configuration files, and package requirements necessary to bootstrap a clean, reproducible data science development environment.

## Project Core Objective
This data pipeline automates the end-to-end extraction, optimization, and enrichment of video transcription data. The system reads streaming line-delimited JSON transcripts via standard input (`stdin`), cleans structural raw formatting, orchestrates semantic enrichment by executing secure remote procedure calls to the Google GenAI `gemini-2.5-flash` model, and streams schema-validated JSON data structures direct to standard output (`stdout`) for downstream data warehouse ingestion.

---

## Prerequisites

Before beginning, ensure you have the following starting point configured:
* An active Ubuntu Server 26.04 VM
* GitHub SSH keys configured on the VM
* Stable outbound network access to Google GenAI API gateways (`https://generativelanguage.googleapis.com`)

## Repository Structure

```text
.
├── .github/
│   └── workflows/
│       └── ci.yml          # Parallelized multi-version parallel CI test matrix 
├── README.md               # Project documentation and setup guide
├── makefile                # Automation tasks for Python environment management
├── requirements.txt        # Python core library dependencies (pandas, numpy, pytest, etc.)
├── bin/
│   └── enrich_transcripts.py  # Core LLM stream enrichment data pipeline module
└── scripts/
    ├── init.sh             # Base system package installer (make, tree, python venv)
    └── init_git_creds.sh   # Global Git identity configuration script
```

## Set Up Instructions

When your VM is set up, make a clone of my repository on Github. Then, clone your new repository and navigate into the root directory on the VM:

```bash
git clone git@github.com:/<user name>/DS-5111.git
cd DS-5111
```

Please note, I am assuming your repo will be named the same as mine. Once it has been cloned, use nano to open init_git_creds.sh and edit the username and user email to be the ones associated with your account.

Next, intialize the scripts to prepare your virtual environment by executing these commands:

```bash
chmod +x scripts/init.sh scripts/init_git_creds.sh
bash scripts/init.sh
bash scripts/init_git_creds.sh
```

To confirm the set up worked we need to run two quick tests:

* Test for init.sh: Type tree in your terminal. If the script worked, it will output your directory structure instead of a "command not found" error.

* Test for init_git_creds.sh: Review the terminal output after running the script. It should output your github email and username.

Then, run the following command to automatically create your virtual environment and install the necessary dependencies:

```bash
make env
make update
```

This triggers the creation of the environment and references requirements.txt to install dependencies. We will then activate the environment and confirm that the required packages are installed by typing

```bash
. env/bin/activate
pip list
```

You have now set up the virtual environment for DS 5111.

## Environment Configuration Variables

The data pipeline relies on a secure environment file for live infrastructure connectivity. You must provision a local file named `.env` in the root of the project directory to prevent structural `403 PERMISSION_DENIED` runtime crashes during live execution.

| Variable Name | Required / Optional | Data Type | Production Target Endpoint / Purpose |
| :--- | :--- | :--- | :--- |
| `GEMINI_API_KEY` | **Required** | Secret String | Authenticates live RPC streaming payloads against the `gemini-2.5-flash` API gateway. |
| `CI` | *Optional* | Boolean | Automatically evaluated by the Makefile runner to toggle between local `env/bin/` paths and GitHub Actions parallel runners. |

To configure your API token safely, create the local configuration file:
```bash
nano .env
```
Paste your secure Google AI Studio token into it. (Note: .env is explicitly ignored inside your .gitignore configuration to prevent accidental credential exposures)

## Verify the Architectgure Quality Gates

To confirm your newly provisioned architecture is fully operational, stable, and completely compliant with local engineering criteria, run your standardized Makefile quality targets:

1. Execute Code Quality & Linting Inspections
Verify that your syntax, docstrings, and parameter mapping scores conform to the gating requirements (aiming for a perfect 10.00/10 mark):
```bash
make lint
```

2. Run the Full Functional Test Engine Suite
Trigger your local automated testing harness to evaluate system components under mock network conditions, confirming environmental skips (@pytest.mark.skipif), expected edge cases (@pytest.mark.xfail), and parameterized inputs function accurately:
```bash
make test
```

3. Verify End-to-End Live Stream Pipelines
Run the production pipeline execution script manually using mock datasets to guarantee that standard output streaming and schema constraint engine layers are green:
```bash
make run
```

## Further updates

To make updates and push them to Github use the following code:

```bash
git add <name of file or files>
git commit -m "<insert your update message>"
git push
```
For updates that are made in Github, navigate to the root repo folder and run the following command to update your VM:

```bash
git pull
```
** EOF **
