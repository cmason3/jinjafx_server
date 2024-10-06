FROM docker.io/library/python:3.13-rc-slim AS BUILD

ARG BRANCH main

RUN set -eux; \

apt-get update; \
apt-get install -y --no-install-recommends wget git build-essential; \

wget -P /tmp https://github.com/jgm/pandoc/releases/download/3.5/pandoc-3.5-1-amd64.deb; \
dpkg -i /tmp/pandoc-3.5-1-amd64.deb; \

python3 -m venv /opt/jinjafx; \
/opt/jinjafx/bin/python3 -m pip install --upgrade git+https://github.com/cmason3/jinjafx_server.git@${BRANCH} lxml; \
/opt/jinjafx/bin/python3 -m pip uninstall -y pip


FROM docker.io/library/python:3.13-rc-slim

COPY --from=BUILD /opt/jinjafx /opt/jinjafx
COPY --from=BUILD /usr/bin/pandoc /usr/bin/pandoc

ENV VIRTUAL_ENV /opt/jinjafx
ENV PATH /opt/jinjafx/bin:${PATH}

ENTRYPOINT [ "python3", "-u", "-m", "jinjafx_server", "-s", "-l", "0.0.0.0", "-p", "8080" ]
