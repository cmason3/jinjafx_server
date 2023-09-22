FROM docker.io/library/python:3.11-slim AS BUILD

ARG BRANCH="main"

RUN set -eux; \

apt-get update; \
apt-get install -y --no-install-recommends git; \

python3 -m venv --copies /opt/jinjafx; \
/opt/jinjafx/bin/python3 -m pip install --upgrade git+https://github.com/cmason3/jinjafx_server.git@${BRANCH} lxml; \
/opt/jinjafx/bin/python3 -m pip uninstall -y pip


FROM scratch

ENV LD_LIBRARY_PATH=/usr/local/lib

COPY --from=BUILD /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=BUILD /usr/local/lib/libpython3* /usr/local/lib/
COPY --from=BUILD /lib/x86_64-linux-gnu/* /lib/x86_64-linux-gnu/
COPY --from=BUILD /lib64/* /lib64/
COPY --from=BUILD --chown=99:99 /opt/jinjafx /opt/jinjafx

USER 99:99

ENTRYPOINT [ "/opt/jinjafx/bin/python3", "-u", "-m", "jinjafx_server", "-s", "-l", "0.0.0.0", "-p", "8080" ]
