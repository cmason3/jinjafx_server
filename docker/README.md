## Docker/Podman for JinjaFx Server

JinjaFx Server will always be available in Docker Hub at [https://hub.docker.com/repository/docker/cmason3/jinjafx_server](https://hub.docker.com/repository/docker/cmason3/jinjafx_server) - the `latest` tag will always refer to the latest released version.

The following commands (using sudo) will launch a container for JinjaFx Server which listens on localhost on port 8080.

The first step is to create a local user which maps to the UID/GID of the non-root user inside the container - we will also create a persistent logfile outside of the container and we will need to give the local user access to it (as we are using a persistent logfile we have also disabled logging inside the container using `--log-driver=none`).

```
groupadd -g 99 -r jinjafx
useradd -u 99 -g 99 -r jinjafx

touch /var/log/jinjafx.log
chown root:jinjafx /var/log/jinjafx.log
chmod 664 /var/log/jinjafx.log
```

### JinjaFx Server

```
podman create --name jinjafx --tz=local --log-driver=none -v /var/log/jinjafx.log:/var/log/jinjafx.log:Z -p 127.0.0.1:8080:8080 docker.io/cmason3/jinjafx_server:latest

podman generate systemd -n --restart-policy=always jinjafx | tee /etc/systemd/system/jinjafx.service 1>/dev/null

systemctl daemon-reload
systemctl enable --now jinjafx
```

Once the `jinjafx` container is running you should be able to point your browser at http://127.0.0.1:8080 and it will be passed through to the JinjaFx Server (although the preferred approach is running HAProxy in front of JinjaFx Server so it can deal with TLS termination with HTTP/2 or HTTP/3). I have also included a `jinjafx-run.sh` helper script, which automates the running and updating of the JinjaFx container - if you want to run or update the running container to the container image tagged as "latest" then you can run the following command (it assumes Podman):

```
sudo sh jinjafx-run.sh latest
```
