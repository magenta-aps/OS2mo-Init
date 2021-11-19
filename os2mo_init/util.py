# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from typing import cast

import click
from pydantic import AnyHttpUrl
from pydantic import parse_obj_as
from pydantic import ValidationError
from ra_utils.generate_uuid import uuid_generator


def validate_url(ctx: click.Context, param: Any, value: Any) -> AnyHttpUrl:
    try:
        return cast(AnyHttpUrl, parse_obj_as(AnyHttpUrl, value))
    except ValidationError as e:
        raise click.BadParameter(str(e))


generate_uuid = uuid_generator(base="OS2MO")
