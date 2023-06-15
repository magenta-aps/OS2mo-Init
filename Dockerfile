# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
FROM python:3.11@sha256:2dd2f9000021839e8fba0debd8a2308c7e26f95fdfbc0c728eeb0b5b9a8c6a39

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
