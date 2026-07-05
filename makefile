default:
	@cat makefile

env:
	python3 -m venv env; . env/bin/activate; pip install --upgrade pip

update: env
	. env/bin/activate; pip install -r requirements.txt

lint:
	. env/bin/activate && pylint bin/clean_ids.py bin/enrich_transcripts.py bin/enrich_transcripts_oop.py bin/extract_transcripts.py

test_enrich:
	@. env/bin/activate && cat mock_transcripts.jsonl | python -u bin/enrich_transcripts.py | python tests/validate_schema.py

test_enrich_oop:
	. env/bin/activate && python3 -m pytest -vv tests/test_enrich_transcripts_oop.py

test: lint
	. env/bin/activate && python3 -m pytest -vv tests --ignore=tests/test_enrich_transcripts.py

clean:
	rm -rf __pycache__ bin/__pycache__ lib/__pycache__ tests/__pycache__ .pytest_cache
	rm -f logs/*.log
