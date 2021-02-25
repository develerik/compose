lint:
	@docker run -e RUN_LOCAL=true -e VALIDATE_ALL_CODEBASE=false -e VALIDATE_PYTHON_PYTHON=true -e VALIDATE_PYTHON_PYLINT=true -e VALIDATE_MD=true -e VALIDATE_YAML=true -v $(PWD):/tmp/lint github/super-linter
