import pathlib, re
from setuptools import setup

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()
README = re.sub(r'<p.+</p>', '', README[README.find('#'):])

setup(
  name="jinjafx_server",
  version="21.12.1",
  description="JinjaFx Server - Jinja2 Templating Tool",
  long_description=README,
  long_description_content_type="text/markdown",
  url="https://github.com/cmason3/jinjafx_server",
  author="Chris Mason",
  author_email="chris@netnix.org",
  license="MIT",
  classifiers=[
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3"
  ],
  packages=["jinjafx_server"],
  include_package_data=True,
  package_data={'': ['www/*']},
  install_requires=["jinjafx", "netaddr", "requests"],
  entry_points={
    "console_scripts": [
      "jinjafx_server=jinjafx_server:main",
    ]
  }
)
