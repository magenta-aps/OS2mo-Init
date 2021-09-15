# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
import click
from pydantic import AnyHttpUrl
from ra_utils.async_to_sync import async_to_sync
from ra_utils.generate_uuid import uuid_generator
from raclients.lora import ModelClient as LoRaModelClient

from .initialisers import ensure_default_classes
from .initialisers import ensure_default_facets
from .initialisers import ensure_root_organisation
from .util import validate_url

# from raclients.modelclientbase import common_session_factory
# from .util import LoraTokenSettings


@click.command(
    context_settings=dict(
        max_content_width=120,
    ),
    epilog=(
        "In addition to the listed environment variables, the program accepts "
        "parameters from environment variables using the format "
        "'OS2MO_INIT_<OPTION>'; for example 'OS2MO_INIT_MUNICIPALITY_CODE'. "
        "Furthermore, the following environment variables are used to "
        "establish a connection to LoRa:"
        "\n\n\b\n"  # prevent click rewrapping
        "CLIENT_ID [default: mo]\n"
        "CLIENT_SECRET [required]\n"
        "AUTH_REALM [default: lora]\n"
        "AUTH_SERVER [default: http://localhost:8080/auth]\n"
    ),
)
@click.option(
    "--lora-url",
    help="Address of the LoRa host",
    callback=validate_url,
    default="http://localhost:8080",
    show_default=True,
    envvar="LORA_URL",
    show_envvar=True,
)
@click.option(
    "--root-org-name",
    help="Name of the root organisation",
    type=click.STRING,
    default="Magenta Aps",
    show_default=True,
    envvar="ROOT_ORG_NAME",
    show_envvar=True,
)
@click.option(
    "--municipality-code",
    help="Municipality code of the root organisation",
    type=click.INT,
    default=1234,
    show_default=True,
)
@async_to_sync
async def run(
    lora_url: AnyHttpUrl,
    root_org_name: str,
    municipality_code: int,
) -> None:
    client = LoRaModelClient(
        base_url=lora_url,
        # TODO: Uncomment when https://git.magenta.dk/rammearkitektur/os2mo/-/tree/feature/45561-lora-auth is merged  # noqa: E501
        # session_factory=common_session_factory(token_settings=LoraTokenSettings()),
    )
    generate_uuid = uuid_generator(base=root_org_name)
    async with client.context():
        root_organisation_uuid = await ensure_root_organisation(
            client=client,
            name=root_org_name,
            municipality_code=municipality_code,
        )
        await ensure_default_facets(
            client=client,
            organisation_uuid=root_organisation_uuid,
            generate_uuid=generate_uuid,
        )
        await ensure_default_classes(
            client=client,
            organisation_uuid=root_organisation_uuid,
            generate_uuid=generate_uuid,
        )
