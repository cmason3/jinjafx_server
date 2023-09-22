FROM docker.io/library/python:3.11-slim

ARG BRANCH="main"

ENV PATH ${PATH}:/opt/jinjafx/.local/bin

RUN set -eux; \

apt-get update; \
apt-get install -y --no-install-recommends git; \

groupadd -g 99 -r jinjafx; \
useradd -m jinjafx -u 99 -g 99 -d /opt/jinjafx -k /dev/null; \

# runuser -u jinjafx -- python3 -m pip --disable-pip-version-check --no-cache-dir install --user jinjafx-server
runuser -u jinjafx -- python3 -m pip --disable-pip-version-check --no-cache-dir install --user git+https://github.com/cmason3/jinjafx_server.git@${BRANCH} lxml; \

apt-get purge -y --auto-remove git; \
rm -rf /var/lib/apt/lists/*

USER jinjafx

WORKDIR /opt/jinjafx

ENTRYPOINT [ "python3", "-u", ".local/bin/jinjafx_server", "-s", "-l", "0.0.0.0", "-p", "8080" ]
