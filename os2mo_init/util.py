# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
from typing import Any
from typing import cast

import click
from pydantic import AnyHttpUrl
from pydantic import Field
from pydantic import parse_obj_as
from pydantic import ValidationError
from ra_utils.headers import TokenSettings


def validate_url(ctx: click.Context, param: Any, value: Any) -> AnyHttpUrl:
    try:
        return cast(AnyHttpUrl, parse_obj_as(AnyHttpUrl, value))
    except ValidationError as e:
        raise click.BadParameter(str(e))


class LoraTokenSettings(TokenSettings):
    """
    RA Utils TokenSettings, but with defaults for LoRa.
    """

    client_secret: str
    auth_realm: str = "lora"
    auth_server: AnyHttpUrl = Field("http://localhost:8081/auth")
