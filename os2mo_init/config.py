# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import logging
from io import TextIOWrapper
from typing import ItemsView

import structlog
import yaml
from pydantic import BaseModel


class ConfigRootOrganisation(BaseModel):
    municipality_code: int | None


class ConfigClass(BaseModel):
    title: str
    scope: str | None
    it_system: str | None


class ConfigFacet(BaseModel):
    __root__: dict[str, ConfigClass]

    def items(self) -> ItemsView[str, ConfigClass]:
        return self.__root__.items()


class Config(BaseModel):
    root_organisation: ConfigRootOrganisation | None
    facets: dict[str, ConfigFacet] | None
    it_systems: dict[str, str] | None


def get_config(config_file: TextIOWrapper) -> Config:
    config_yaml = yaml.safe_load(config_file)
    config = Config.parse_obj(config_yaml)
    return config


def set_log_level(log_level_name: str) -> None:
    log_level_value = logging.getLevelName(log_level_name)
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(log_level_value)
    )
