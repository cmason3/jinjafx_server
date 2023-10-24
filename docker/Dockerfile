FROM docker.io/library/python:3.12-slim AS BUILD

ARG BRANCH="main"

RUN set -eux; \

apt-get update; \
apt-get install -y --no-install-recommends wget git build-essential; \

wget -P /tmp https://github.com/jgm/pandoc/releases/download/3.1.8/pandoc-3.1.8-1-amd64.deb; \
dpkg -i /tmp/pandoc-3.1.8-1-amd64.deb; \

python3 -m venv /opt/jinjafx; \
/opt/jinjafx/bin/python3 -m pip install --upgrade git+https://github.com/cmason3/jinjafx_server.git@${BRANCH} lxml; \
/opt/jinjafx/bin/python3 -m pip uninstall -y pip


FROM docker.io/library/python:3.12-slim

COPY --from=BUILD --chown=99:99 /opt/jinjafx /opt/jinjafx
COPY --from=BUILD --chown=99:99 /usr/bin/pandoc /usr/bin/pandoc

USER 99:99

ENTRYPOINT [ "/opt/jinjafx/bin/python3", "-u", "-m", "jinjafx_server", "-s", "-l", "0.0.0.0", "-p", "8080" ]
