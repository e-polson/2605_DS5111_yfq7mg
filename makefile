ifdef CI
    PYTHON = python3
    PIP = pip
else
    ENV_DIR = env
    PYTHON = $(ENV_DIR)/bin/python3
    PIP = $(ENV_DIR)/bin/pip
endif

default:
	@cat makefile

env:
	@if [ ! -d "env" ]; then \
		python3 -m venv env; \
		env/bin/pip install --upgrade pip; \
	fi

update:
	$(PIP) install -r requirements.txt

lint:
	$(PYTHON) -m pylint bin/ lib/ tests/ --min-similarity-lines=25 # add because of files in tests/ directory

test: lint
	$(PYTHON) -m pytest tests/

run:
	@echo "Executing pipeline end-to-end..."
	@if [ ! -s mock_transcripts.jsonl ]; then \
		echo "Error: mock_transcripts.jsonl is missing or empty!"; \
		exit 1; \
	fi
	@cat mock_transcripts.jsonl | $(PYTHON) -u bin/enrich_transcripts.py | $(PYTHON) tests/validate_schema.py

test_enrich:
	@cat mock_transcripts.jsonl | $(PYTHON) -u bin/enrich_transcripts.py | $(PYTHON) tests/validate_schema.py

test_enrich_oop:
	$(PYTHON) -m pytest -vv tests/test_enrich_transcripts_oop.py

clean:
	rm -rf __pycache__ bin/__pycache__ lib/__pycache__ tests/__pycache__ .pytest_cache
	rm -f logs/*.log


.PHONY: load
load:
	@echo "Initiating Cloud Data Warehouse Synchronizer Node..."
	cat data/enriched_transcripts.jsonl | python bin/load_snowflake.py
