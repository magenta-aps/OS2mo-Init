# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
FROM python:3.11@sha256:188e45cf9f0a2e6404666a2eaf04ef6e5c7a2bf6e34c28bca247dd82e5556fb6

WORKDIR /app

ENV POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python --

COPY pyproject.toml poetry.lock* ./

RUN /opt/poetry/bin/poetry install --no-root --no-dev

COPY . ./
COPY config.default.yml /config/config.yml

ENTRYPOINT ["python", "-m", "os2mo_init"]
