import pathlib, re
from setuptools import setup

for line in open('jinjafx_server.py'):
  if line.startswith('__version__'):
    exec(line)
    break

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
README = re.sub(r'^.*\[<img', '[<img', README, flags=re.DOTALL)
README = re.sub(r'<p.+?</p>', '', README, flags=re.DOTALL)    

setup(
  name="jinjafx_server",
  version=__version__,
  python_requires=">=3.6",
  description="JinjaFx Server - Jinja2 Templating Tool",
  long_description=README,
  long_description_content_type="text/markdown",
  url="https://github.com/cmason3/jinjafx_server",
  author="Chris Mason",
  author_email="chris@netnix.org",
  license="MIT",
  classifiers=[
    "Development Status :: 5 - Production/Stable",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3"
  ],
  packages=["jinjafx_server"],
  include_package_data=True,
  package_data={'': ['www/*']},
  install_requires=["jinjafx>=1.13.0", "requests", "cmarkgfm>=0.5.0", "emoji", "func_timeout"],
  entry_points={
    "console_scripts": [
      "jinjafx_server=jinjafx_server:main",
    ]
  }
)
