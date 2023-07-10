# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from io import TextIOWrapper

import click
from pydantic import AnyHttpUrl
from ra_utils.async_to_sync import async_to_sync
from structlog import get_logger

from os2mo_init import initialisers
from os2mo_init import mo
from os2mo_init.config import get_config
from os2mo_init.config import set_log_level
from os2mo_init.util import validate_url
from raclients.graph.client import GraphQLClient

from typing import Any
from typing import cast

import click
from pydantic import AnyHttpUrl
from pydantic import parse_obj_as
from pydantic import ValidationError

logger = get_logger(__name__)


def validate_url(ctx: click.Context, param: Any, value: Any) -> AnyHttpUrl:
    try:
        return cast(AnyHttpUrl, parse_obj_as(AnyHttpUrl, value))
    except ValidationError as e:
        raise click.BadParameter(str(e))



@click.command(
    context_settings=dict(
        show_default=True,
        max_content_width=120,
    ),
)
@click.option(
    "--auth-server",
    help="Keycloak authentication server.",
    required=True,
    callback=validate_url,
    envvar="AUTH_SERVER",
    show_envvar=True,
)
@click.option(
    "--mo-url",
    help="OS2mo URL.",
    required=True,
    callback=validate_url,
    envvar="MO_URL",
    show_envvar=True,
)
@click.option(
    "--client-id",
    help="Client ID used to authenticate against OS2mo.",
    required=True,
    default="dipex",
    envvar="CLIENT_ID",
    show_envvar=True,
)
@click.option(
    "--client-secret",
    help="Client secret used to authenticate against OS2mo.",
    required=True,
    envvar="CLIENT_SECRET",
    show_envvar=True,
)
@click.option(
    "--auth-realm",
    help="Keycloak realm for OS2mo authentication.",
    required=True,
    default="mo",
    envvar="AUTH_REALM",
    show_envvar=True,
)
@click.option(
    "--config-file",
    help="Path to initialisation config file.",
    type=click.File(),
    required=True,
    default="/config/config.yml",
    envvar="CONFIG_FILE",
    show_envvar=True,
)
@click.option(
    "--log-level",
    help="Set the application log level",
    type=click.Choice(
        ["CRITICAL", "FATAL", "ERROR", "WARN", "WARNING", "INFO", "DEBUG", "NOTSET"],
        case_sensitive=False,
    ),
    default="INFO",
    envvar="LOG_LEVEL",
    show_envvar=True,
)
@async_to_sync
async def run(
    auth_server: AnyHttpUrl,
    mo_url: AnyHttpUrl,
    client_id: str,
    client_secret: str,
    auth_realm: str,
    config_file: TextIOWrapper,
    log_level: str,
) -> None:

    set_log_level(log_level)
    logger.info("Application startup")

    config = get_config(config_file)
    
    logger.debug("Creating clients...")

    mo_graphql_client = GraphQLClient(
        url=f"{mo_url}/graphql/v7",
        client_id=client_id,
        client_secret=client_secret,
        auth_realm=auth_realm,
        auth_server=auth_server,
    )
    async with mo_graphql_client as mo_graphql_session:
        # Root Organisation

        logger.info("Handling root organisation")

        root_organisation_uuid = await mo.get_root_org(clients.mo_graphql_session)
        logger.debug("Existing root organisation", uuid=root_organisation_uuid)

        if config.root_organisation is not None:
            root_organisation_uuid = await initialisers.ensure_root_organisation(
                lora_model_client=clients.lora_model_client,
                existing_uuid=root_organisation_uuid,
                **config.root_organisation.dict(),
            )
        if root_organisation_uuid is None:
            raise ValueError(
                "No root organisation configuration supplied, but none exist in MO."
                "Unable to continue."
            )

        # Facets and Classes
        if config.facets is not None:
            facet_user_keys = config.facets.keys()
            facets = await initialisers.ensure_facets(
                mo_client=clients.mo_client,
                lora_model_client=clients.lora_model_client,
                organisation_uuid=root_organisation_uuid,
                user_keys=facet_user_keys,
            )
            facet_uuids = dict(zip(facet_user_keys, (f.uuid for f in facets)))
            await initialisers.ensure_classes(
                mo_client=clients.mo_client,
                mo_model_client=clients.mo_model_client,
                organisation_uuid=root_organisation_uuid,
                facet_classes_config=config.facets,
                facet_uuids=facet_uuids,
            )

        # IT Systems
        if config.it_systems is not None:
            await initialisers.ensure_it_systems(
                mo_client=clients.mo_client,
                lora_model_client=clients.lora_model_client,
                organisation_uuid=root_organisation_uuid,
                it_systems_config=config.it_systems,
            )
