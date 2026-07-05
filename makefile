ENV = env
PYTHON = $(ENV)/bin/python3
PIP = $(ENV)/bin/pip

default:
	@cat Makefile

$(ENV):
	python3 -m venv $(ENV)
	$(PIP) install --upgrade pip

update: $(ENV)
	$(PIP) install -r requirements.txt

lint: $(ENV)
	$(PYTHON) -m pylint bin/ lib/ tests/

test_enrich: $(ENV)
	@cat mock_transcripts.jsonl | $(PYTHON) -u bin/enrich_transcripts.py | $(PYTHON) tests/validate_schema.py

test_enrich_oop: $(ENV)
	$(PYTHON) -m pytest -vv tests/test_enrich_transcripts_oop.py

test: lint
	$(PYTHON) -m pytest tests/

clean:
	rm -rf __pycache__ bin/__pycache__ lib/__pycache__ tests/__pycache__ .pytest_cache
	rm -f logs/*.log

