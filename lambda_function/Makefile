all: imports lambda

imports: clean-imports
	python3 -m pip --disable-pip-version-check --no-cache-dir install -t python jinjafx
	@find python/ -name "*.dist-info" -type d -exec rm -r {} +
	@rm -r python/bin
	@find . -type d -exec chmod 755 {} +
	@find . -type f -exec chmod 644 {} +
	zip jinjafx_imports.zip -r python/*

lambda: clean-lambda
	@find . -type d -exec chmod 755 {} +
	@find . -type f -exec chmod 644 {} +
	zip jinjafx_lambda.zip lambda_function.py www/*

clean: clean-imports clean-lambda

clean-imports:
	@rm -rf python jinjafx_imports.zip

clean-lambda:
	@rm -rf jinjafx_lambda.zip
