<!--
SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
SPDX-License-Identifier: MPL-2.0
-->

# OS2mo Init


## Usage
The primary usage of the tool is to initialise OS2mo's database with a root organisation, all required classes,
recommended facets, and IT systems.
```text
Usage: python -m os2mo_init [OPTIONS]

Options:
  --mo-url TEXT                   OS2mo URL.  [env var: MO_URL; required]
  --auth-server TEXT              Keycloak authentication server.  [env var: AUTH_SERVER; required]
  --auth-realm TEXT               Keycloak realm for OS2mo authentication.  [env var: AUTH_REALM; required]
  --client-id TEXT                Client ID used to authenticate against OS2mo.  [env var: CLIENT_ID; required]
  --client-secret TEXT            Client secret used to authenticate against OS2mo.  [env var: CLIENT_SECRET; required]
  --config-file FILENAME          Path to initialisation config file.  [env var: CONFIG_FILE; default: /config/config.yml; required]
  --log-level [CRITICAL|FATAL|ERROR|WARN|WARNING|INFO|DEBUG|NOTSET] Set the application log level  [env var: LOG_LEVEL; default: INFO]
  --help                          Show this message and exit.
```

For development, most users will probably want to use Docker Compose as follows:
```yaml
services:
  mo-init:
    image: magentaaps/os2mo-init:latest
    environment:
      MO_URL: "http://mo"
      AUTH_SERVER: "http://keycloak:8080/auth"
      AUTH_REALM: "mo"
      CLIENT_ID: "d1fec000-baad-c0de-0000-004449504558"
      CLIENT_SECRET: "603f1c82-d012-4d04-9382-dbe659c533fb"
    depends_on:
      mo:
        condition: service_healthy
```
Which will initialise a minimal MO instance using the default configuration file `config.default.yml`. Modifying the
configuration is as easy as copying the default `config.default.yml` from here to `init.config.yml` in your repo and
extending Docker Compose as follows:
```yaml
services:
  mo-init:
    volumes:
      - type: bind
        source: ./init.config.yml
        target: /config/config.yml
        read_only: true
```

Ad-hoc usage can be done as follows:
```bash
docker run --rm --mount type=bind,source="$(pwd)"/init.config.yml,destination=/config/config.yml --network=host magentaaps/os2mo-init:latest --mo-url="http://localhost:5000" --auth-server="http://localhost:8090/auth" --client-id=d1fec000-baad-c0de-0000-004449504558 --client-secret=hunter2 --auth-realm=mo
```
Optionally with the `--network=host` or `--network=os2mo_default` docker flag.


## Deployment
Initialisation setup is configured using a configuration file; `/config/config.yml` by default. The provided Docker
image copies the default configuration [config.default.yml](config.default.yml) to this location in the image, which
sets up a minimal MO instance.

To modify the configuration in a Kubernetes cluster, first define a `ConfigMap` as follows:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: os2mo-init-config
data:
  config: |
    root_organisation:
      ...
    facets:
      ...
```
Then connect it to the deployment or pod:
```yaml
spec:
  containers:
    - name: mo-init
      image: magentaaps/os2mo-init:latest
      volumeMounts:
        - name: os2mo-init-config-volume
          mountPath: /config
          readOnly: true
  volumes:
    - name: os2mo-init-config-volume
      configMap:
        name: os2mo-init-config
        items:
          - key: config
            path: config.yml
```


## Build
```commandline
docker build . -t os2mo-init
```
Which yields:
```text
...
Successfully built ...
Successfully tagged os2mo-init:latest
```
After which you can run:
```commandline
docker run --rm os2mo-init:latest --help
```


## Versioning
This project uses [Semantic Versioning](https://semver.org/) with the following strategy:
- MAJOR: Incompatible changes to existing commandline interface.
- MINOR: Backwards compatible updates to commandline interface.
- PATCH: Backwards compatible bug fixes.


## Authors
Magenta ApS <https://magenta.dk>


## License
- This project: [MPL-2.0](LICENSES/MPL-2.0.txt)

This project uses [REUSE](https://reuse.software) for licensing. All licenses can be found in the [LICENSES folder](LICENSES/) of the project.
