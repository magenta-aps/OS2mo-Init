# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from io import TextIOWrapper
from typing import ItemsView
from typing import Optional

import yaml
from pydantic import BaseModel, BaseSettings


class ConfigRootOrganisation(BaseModel):
    name: str
    user_key: str
    municipality_code: Optional[int]


class ConfigClass(BaseModel):
    title: str
    scope: str


class ConfigFacet(BaseModel):
    __root__: dict[str, ConfigClass]

    def items(self) -> ItemsView[str, ConfigClass]:
        return self.__root__.items()


class Config(BaseModel):
    root_organisation: Optional[ConfigRootOrganisation]
    facets: Optional[dict[str, ConfigFacet]]
    it_systems: Optional[dict[str, str]]


def get_config(config_file: TextIOWrapper) -> Config:
    config_yaml = yaml.safe_load(config_file)
    config = Config.parse_obj(config_yaml)
    return config


class Settings(BaseSettings):
    log_level: str = "INFO"


settings = Settings()
