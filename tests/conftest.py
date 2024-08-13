# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path

import pytest
from pytest import MonkeyPatch


@pytest.fixture
async def config_file(tmp_path: Path, monkeypatch: MonkeyPatch) -> Path:
    file = tmp_path.joinpath("init.config.yaml")
    file.touch()
    monkeypatch.setenv("CONFIG_FILE", str(file))
    return file
