FROM docker.io/library/python:3.10-slim

ENV PATH ${PATH}:/opt/jinjafx/.local/bin

RUN set -eux; \

groupadd -g 99 -r jinjafx; \
useradd -m jinjafx -u 99 -g 99 -d /opt/jinjafx -k /dev/null; \

runuser -u jinjafx -- python3 -m pip --disable-pip-version-check --no-cache-dir install --user --upgrade 'jinja2==3.0.*' 'ansible-core==2.12.*' jinjafx-server

USER jinjafx

WORKDIR /opt/jinjafx

ENTRYPOINT [ "python3", "-u", ".local/bin/jinjafx_server", "-s", "-l", "0.0.0.0", "-p", "8080" ]
