# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
FROM python:3.11@sha256:85b3d192dddbc96588b719e86991e472b390805a754681a38132de1977d8e429

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VERSION="1.3" \
    POETRY_HOME=/opt/poetry \
    VIRTUAL_ENV="/venv"
ENV PATH="$VIRTUAL_ENV/bin:$POETRY_HOME/bin:$PATH"

# Install poetry in an isolated environment
RUN python -m venv $POETRY_HOME \
    && pip install --no-cache-dir poetry==${POETRY_VERSION}

# Install project in another isolated environment
RUN python -m venv $VIRTUAL_ENV
COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-root

COPY . ./
COPY config.default.yml /config/config.yml

ENTRYPOINT ["python", "-m", "os2mo_init"]
