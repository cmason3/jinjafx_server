## JinjaFx Server as a Container in Kubernetes

JinjaFx Server will always be available in Docker Hub at [https://hub.docker.com/repository/docker/cmason3/jinjafx_server](https://hub.docker.com/repository/docker/cmason3/jinjafx_server) - the `latest` tag will always refer to the latest released version.




```
openssl req -nodes -newkey rsa:2048 -keyout ingress.key -out ingress.csr -subj "/CN={CN}/emailAddress={emailAddress}/O={O}/L={L}/ST={ST}/C={C}" -reqexts SAN -config <(cat /etc/ssl/openssl.cnf <(printf "[SAN]\nsubjectAltName=DNS:*.{CLUSTER}.{DOMAIN}"))
```

```
kubectl create secret generic jinjafx --from-literal=jfx-weblog-key={KEY}
```



The following commands will launch a container for JinjaFx Server which listens on localhost on port 8080.

Rootless Podman has two methods of running, either with root inside the container, which is mapped to the current non-root user outside the container, or if we use `UserNS=keep-id` then we use the current outside non-root user inside the container as well. Running with non-root inside and non-root outside is always preferred from a security perspective and as JinjaFx Server doesn't require root priviledges this is what this does.

For ease of logging, we will also create a persistent logfile outside of the container and will give the local user access to it via a mapped volume (as we are using a persistent logfile we will also disable logging inside the container using `LogDriver=none`).

```
mkdir ~/logs
touch ~/logs/jinjafx.log
```

The following commands require Podman v4.5 or higher and use the new quadlets method of deploying containers via systemd. We are also passing through the `JFX_WEBLOG_KEY` environment variable that we store as a Podman Secret.

```
printf <PASSWORD> | podman secret create jfx_weblog_key -

curl https://raw.githubusercontent.com/cmason3/jinjafx_server/main/podman/jinjafx.container \
  -Os --create-dirs --output-dir ~/.config/containers/systemd

systemctl --user daemon-reload

systemctl --user start jinjafx
```

This will then run the 'jinjafx' container via systemd (and restart on reboot) as the current non-root user. You should be able to point your browser at http://127.0.0.1:8080 and it will be passed through to the JinjaFx Server (although the preferred approach is running HAProxy in front of JinjaFx Server so it can deal with TLS termination with HTTP/2 or HTTP/3).
