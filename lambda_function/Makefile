all: clean
	python3 -m pip --disable-pip-version-check --no-cache-dir install -t lib jinjafx
	@find lib/ -name "*.dist-info" -type d -exec rm -r {} +
	@find . -type d -exec chmod 755 {} +
	@find . -type f -exec chmod 644 {} +
	@rm -r lib/bin
	cd lib; zip ../jinjafx_imports.zip -r *
	zip jinjafx_lambda.zip lambda_function.py www/*

clean:
	@rm -rf lib jinjafx_imports.zip jinjafx_lambda.zip
