ENV = env
PYTHON = $(ENV)/bin/python3
PIP = $(ENV)/bin/pip

default:
	@cat Makefile

env:
	@if [ ! -d "$(ENV_DIR)" ]; then \
		python3 -m venv $(ENV_DIR); \
		$(PIP) install --upgrade pip; \
	fi

update: $(ENV)
	$(PIP) install -r requirements.txt

lint: $(ENV)
	$(PYTHON) -m pylint bin/ lib/ tests/ --min-similarity-lines=25 ##added because of tests/ files

run: $(ENV)
	@echo "Executing pipeline end-to-end..."
	@cat mock_transcripts.jsonl | $(PYTHON) -u bin/enrich_transcripts.py | $(PYTHON) tests/validate_schema.py

test_enrich: $(ENV)
	@cat mock_transcripts.jsonl | $(PYTHON) -u bin/enrich_transcripts.py | $(PYTHON) tests/validate_schema.py

test_enrich_oop: $(ENV)
	$(PYTHON) -m pytest -vv tests/test_enrich_transcripts_oop.py

test: lint
	$(PYTHON) -m pytest tests/

clean:
	rm -rf __pycache__ bin/__pycache__ lib/__pycache__ tests/__pycache__ .pytest_cache
	rm -f logs/*.log

