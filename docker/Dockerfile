FROM docker.io/library/python:3.12-slim AS BUILD

ARG BRANCH="main"

RUN set -eux; \

apt-get update; \
apt-get install -y --no-install-recommends git build-essential; \

python3 -m venv /opt/jinjafx; \
/opt/jinjafx/bin/python3 -m pip install --upgrade git+https://github.com/cmason3/jinjafx_server.git@${BRANCH} lxml; \
/opt/jinjafx/bin/python3 -m pip uninstall -y pip


FROM docker.io/library/python:3.12-slim

COPY --from=BUILD --chown=99:99 /opt/jinjafx /opt/jinjafx

USER 99:99

ENTRYPOINT [ "/opt/jinjafx/bin/python3", "-u", "-m", "jinjafx_server", "-s", "-l", "0.0.0.0", "-p", "8080" ]
