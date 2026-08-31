.PHONY: validate test package clean

validate:
	python3 scripts/validate.py

test:
	python3 -m unittest discover -s tests -v

package: validate test
	python3 scripts/package.py

clean:
	python3 -c 'import shutil; [shutil.rmtree(p, ignore_errors=True) for p in ("dist", "scripts/__pycache__", "tests/__pycache__")]'
