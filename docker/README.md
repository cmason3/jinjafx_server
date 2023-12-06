## Rootless Podman for JinjaFx Server

JinjaFx Server will always be available in Docker Hub at [https://hub.docker.com/repository/docker/cmason3/jinjafx_server](https://hub.docker.com/repository/docker/cmason3/jinjafx_server) - the `latest` tag will always refer to the latest released version.

The following commands will launch a container for JinjaFx Server which listens on localhost on port 8080.

As we are using Rootless Podman we will be running Podman as a non-root user, which will map to the root user inside the container. We will also create a persistent logfile outside of the container and we will need to give the local user access to it via a mapped volume (as we are using a persistent logfile we will also disable logging inside the container using `LogDriver=none`).

```
sudo touch /var/log/jinjafx.log
sudo chgrp ${USER} /var/log/jinjafx.log
sudo chmod 664 /var/log/jinjafx.log
```

### JinjaFx Server

The following commands require Podman v4.5 or higher and use the new quadlets method of deploying containers via systemd:

```
printf <PASSWORD> | podman secret create jfx_weblog_key -

curl https://raw.githubusercontent.com/cmason3/jinjafx_server/main/docker/jinjafx.container -Os --create-dirs --output-dir ~/.config/containers/systemd
systemctl --user daemon-reload

systemctl --user start jinjafx
```

This will then run the 'jinjafx' container via systemd (and restart on reboot) as the current non-root user. You should be able to point your browser at http://127.0.0.1:8080 and it will be passed through to the JinjaFx Server (although the preferred approach is running HAProxy in front of JinjaFx Server so it can deal with TLS termination with HTTP/2 or HTTP/3).
