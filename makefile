default:
	@cat makefile

env:
	python3 -m venv env; . env/bin/activate; pip install --upgrade pip

update:  env
	. env/bin/activate; pip install -r requirements.txt

lint:
	pylint clean_ids.py

test: lint
	python3 -m pytest -vv tests

test_enrich:
	@. env/bin/activate && cat mock_transcripts.jsonl | python -u enrich_transcripts.py | python validate_schema.py
