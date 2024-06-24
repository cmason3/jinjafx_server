## JinjaFx Server as a Container in Kubernetes

JinjaFx Server will always be available in Docker Hub at [https://hub.docker.com/repository/docker/cmason3/jinjafx_server](https://hub.docker.com/repository/docker/cmason3/jinjafx_server) - the `latest` tag will always refer to the latest released version, although it is recommended to use explicit version tags.

The following steps will run JinjaFx Server in a container using Kubernetes Ingress - Ingress is basically the same concept as Virtual Hosting (the default Ingress uses nginx), which works with HTTP and relies on the "Host" header to direct the request to the correct container. In a Virtual Hosting scenario you would typically point different DNS A records towards the same IP, but in our example we are using a Wildcard DNS entry for our whole Kubernetes cluster, e.g:

```
*.{CLUSTER}.{DOMAIN}. 28800   IN      A       {HOST IP}
```

This approach also allows us to use a single wildcard TLS certificate, which covers all containers under the cluster sub-domain. The example Kubernetes Manifest (`kubernetes.yml`) assumes we will be activating the Web Log as well as using a GitHub backed repository to store JinjaFx DataTemplates. Once you have updated `kubernetes.yml` with your deployment specific values you would typically perform the following steps:

### Generate Certificate Signing Request

The following step is used to generate a CSR for your TLS certificiate. The Common Name (CN) isn't actually used as we will be using the "subjectAltName" field as it allows multiple values (you could also use something like Let's Encrypt here, but this is out of scope of this document):

```
openssl req -nodes -newkey rsa:2048 -keyout ingress.key -out ingress.csr -subj "/CN={CN}/emailAddress={emailAddress}/O={O}/L={L}/ST={ST}/C={C}" -reqexts SAN -config <(cat /etc/ssl/openssl.cnf <(printf "[SAN]\nsubjectAltName=DNS:*.{CLUSTER}.{DOMAIN}"))
```

### Generate TLS Secret with Signed Certificate

Once you have a signed certificate you would create a Kubernetes TLS secret called `ingress-tls` using the private key and signed public certificate:

```
kubectl create secret tls ingress-tls --cert=ingress.crt --key=ingress.key
```

### Save Environment Variables as Kubernetes Secrets

To pass the GitHub Token as well as the key used for the Web Log we use Kubernetes secrets that we map into environment variables in the manifest:

```
kubectl create secret generic jinjafx --from-literal=github-token={TOKEN} --from-literal=jfx-weblog-key={KEY}
```

### Apply the Kubernetes Manifest

```
kubectl apply -f kubernetes.yml
```

If everything has worked then you should be able to point your web browser at `https://jinjafx.{CLUSTER}.{DOMAIN}` and it should present you with JinjaFx.
