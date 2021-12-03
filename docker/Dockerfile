FROM docker.io/library/python:3.9-slim

ENV PATH ${PATH}:/opt/jinjafx/.local/bin

RUN set -eux; \

groupadd -g 99 -r jinjafx; \
useradd -m jinjafx -u 99 -g 99 -d /opt/jinjafx -k /dev/null; \

runuser -u jinjafx -- /usr/local/bin/python3 -m pip --disable-pip-version-check --no-cache-dir install --user --upgrade jinja2~=3.0 ansible-core~=2.11 jinjafx-server; \
runuser -u jinjafx -- ansible-galaxy collection install --upgrade ansible.netcommon

USER jinjafx

WORKDIR /opt/jinjafx/jinjafx

ENTRYPOINT [ "/usr/local/bin/python3", "-u", ".local/bin/jinjafx_server.py", "-s", "-l", "0.0.0.0", "-p", "8080" ]
