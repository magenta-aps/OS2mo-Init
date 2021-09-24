<!--
SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
SPDX-License-Identifier: MPL-2.0
-->

# OS2mo Init

OS2mo Initialiser.

## Build
```
docker build . -t os2mo-init
```
Which yields:
```
...
Successfully built ...
Successfully tagged os2mo-init:latest
```
After which you can run:
```
docker run --rm os2mo-init --help
```
Which yields:
```
Usage: os2mo_init [OPTIONS]

Options:
  --lora-url TEXT              Address of the LoRa host  [env var: LORA_URL; default: http://localhost:8080]
  --root-org-name TEXT         Name of the root organisation  [env var: ROOT_ORG_NAME; default: Magenta Aps]
  --municipality-code INTEGER  Municipality code of the root organisation  [default: 1234]
  --help                       Show this message and exit.

  In addition to the listed environment variables, the program accepts parameters from environment variables using
  the format 'OS2MO_INIT_<OPTION>'; for example 'OS2MO_INIT_MUNICIPALITY_CODE'. Furthermore, the following
  environment variables are used to establish a connection to LoRa:

  CLIENT_ID [default: mo]
  CLIENT_SECRET [required]
  AUTH_REALM [default: lora]
  AUTH_SERVER [default: http://localhost:8081/auth]
```

## Usage
The primary usage of the tool is to initialise OS2mo's LoRa database.
```
docker run --rm -e "CLIENT_SECRET=hunter2" os2mo-init
```

## Versioning
This project uses [Semantic Versioning](https://semver.org/) with the following strategy:
- MAJOR: Incompatible changes to existing commandline interface
- MINOR: Backwards compatible updates to commandline interface
- PATCH: Backwards compatible bug fixes

The fileformat is versioned directly, and the version is exported in the file itself.

## Authors

Magenta ApS <https://magenta.dk>

-->
## License
- This project: [MPL-2.0](LICENSES/MPL-2.0.txt)

This project uses [REUSE](https://reuse.software) for licensing. All licenses can be found in the [LICENSES folder](LICENSES/) of the project.
