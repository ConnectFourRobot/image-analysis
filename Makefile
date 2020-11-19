
MODULE := image-analyzer

init:
	pip install -r requirements.txt

run:
	@python -m ${MODULE}

clean:
	rm -rf .pytest_cache .coverage .pytest_cache coverage.xml

.PHONY: init run clean