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
  --auth-server TEXT         Keycloak authentication server.  [env var: AUTH_SERVER; required]
  --mo-url TEXT              OS2mo URL.  [env var: MO_URL; required]
  --client-id TEXT           Client ID used to authenticate against OS2mo.  [env var: CLIENT_ID; default: dipex; required]
  --client-secret TEXT       Client secret used to authenticate against OS2mo.  [env var: CLIENT_SECRET; required]
  --auth-realm TEXT          Keycloak realm for OS2mo authentication.  [env var: AUTH_REALM; default: mo; required]
  --lora-url TEXT            LoRa URL.  [env var: LORA_URL; required]
  --lora-client-id TEXT      Client ID used to authenticate against LoRa.  [env var: LORA_CLIENT_ID; default: dipex; required]
  --lora-client-secret TEXT  Client secret used to authenticate against LoRa.  [env var: LORA_CLIENT_SECRET; required]
  --lora-auth-realm TEXT     Keycloak realm for LoRa authentication.  [env var: LORA_AUTH_REALM; default: lora; required]
  --config-file FILENAME     Path to initialisation config file.  [env var: CONFIG_FILE; default: /config/config.yml; required]
  --help                     Show this message and exit.
```

For development, most users will probably want to use Docker Compose as follows:
```yaml
services:
  mo-init:
    image: magentaaps/os2mo-init:latest
    environment:
      AUTH_SERVER: "http://keycloak:8080/auth"
      MO_URL: "http://mo"
      CLIENT_ID: "dipex"
      CLIENT_SECRET: "603f1c82-d012-4d04-9382-dbe659c533fb"
      AUTH_REALM: "mo"
      LORA_URL: "http://mox"
      LORA_CLIENT_ID: "dipex"
      LORA_CLIENT_SECRET: "a091ed82-6e82-4efc-a8f0-001e2b127853"
      LORA_AUTH_REALM: "lora"
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
    facets:
      org_unit_address_type:
        PhoneUnit:
          title: "CVR"
          scope: "CVR"
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
docker run --rm os2mo-init --help
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
