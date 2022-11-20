#!/usr/bin/sh

# AWS_S3_URL="<name>.s3.<region>.amazonaws.com"
# AWS_ACCESS_KEY="<aws_access_key>"
# AWS_SECRET_KEY="<aws_secret_key>"

ARGS="-rl 5/20s -logfile /var/log/jinjafx.log"

if [ "$(id -u)" != "0" ]; then
  echo 'requires root'
elif [ -z "$1" ]; then
  echo 'usage: jinjafx-run.sh <tag>'
else
  set -e
  echo 'Pulling Container Image...'
  podman pull docker.io/cmason3/jinjafx_server:$1
  set +e
  echo

  echo 'Stopping JinjaFx...'
  systemctl stop jinjafx 1>/dev/null
  echo

  echo 'Removing JinjaFx Container...'
  podman rm jinjafx 2>/dev/null
  echo

  set -e

  echo 'Creating JinjaFx Container...'
  if [ -n "$AWS_S3_URL" ]; then
    podman create --name jinjafx --pull=never --tz=local -v /var/log/jinjafx.log:/var/log/jinjafx.log:Z -e AWS_ACCESS_KEY=${AWS_ACCESS_KEY} -e AWS_SECRET_KEY=${AWS_SECRET_KEY} -p 127.0.0.1:8080:8080 docker.io/cmason3/jinjafx_server:$1 -s3 ${AWS_S3_URL} ${ARGS}
  else
    podman create --name jinjafx --pull=never --tz=local -v /var/log/jinjafx.log:/var/log/jinjafx.log:Z -p 127.0.0.1:8080:8080 docker.io/cmason3/jinjafx_server:$1 ${ARGS}
  fi
  echo

  echo 'Updating /etc/systemd/system/jinjafx.service...'
  podman generate systemd -n --restart-policy=always jinjafx | tee /etc/systemd/system/jinjafx.service 1>/dev/null
  systemctl daemon-reload
  echo

  echo 'Starting JinjaFx...'
  systemctl enable --now jinjafx

  podman ps -a
fi
