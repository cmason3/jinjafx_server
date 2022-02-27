all: clean
	python3 -m pip --disable-pip-version-check --no-cache-dir install -t lib jinjafx
	@find lib/ -name "*.dist-info" -type d -exec rm -r {} +
	@find . -type d -exec chmod 755 {} +
	@find . -type f -exec chmod 644 {} +
	@rm -r lib/bin
	zip jinjafx_lambda.zip lambda_function.py www/* lib/*

clean:
	@rm -rf lib jinjafx_lambda.zip
