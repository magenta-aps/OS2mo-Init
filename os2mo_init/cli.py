# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from io import TextIOWrapper
from typing import Any
from typing import cast

import click
from pydantic import AnyHttpUrl
from pydantic import parse_obj_as
from pydantic import ValidationError
from ra_utils.async_to_sync import async_to_sync
from raclients.graph.client import GraphQLClient
from structlog import get_logger

from os2mo_init.classes import ensure_classes
from os2mo_init.config import get_config
from os2mo_init.config import set_log_level
from os2mo_init.facets import ensure_facets
from os2mo_init.it_systems import ensure_it_systems
from os2mo_init.root_org import ensure_root_organisation

logger = get_logger(__name__)


def validate_url(ctx: click.Context, param: Any, value: Any) -> AnyHttpUrl:
    try:
        return cast(AnyHttpUrl, parse_obj_as(AnyHttpUrl, value))
    except ValidationError as e:
        raise click.BadParameter(str(e))


@click.command(  # type: ignore
    context_settings=dict(
        show_default=True,
        max_content_width=120,
    ),
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
    "--auth-server",
    help="Keycloak authentication server.",
    required=True,
    callback=validate_url,
    envvar="AUTH_SERVER",
    show_envvar=True,
)
@click.option(
    "--auth-realm",
    help="Keycloak realm for OS2mo authentication.",
    required=True,
    envvar="AUTH_REALM",
    show_envvar=True,
)
@click.option(
    "--client-id",
    help="Client ID used to authenticate against OS2mo.",
    required=True,
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
    graphql_client = GraphQLClient(
        url=f"{mo_url}/graphql/v20",
        client_id=client_id,
        client_secret=client_secret,
        auth_realm=auth_realm,
        auth_server=auth_server,
        execute_timeout=30,
        httpx_client_kwargs=dict(
            timeout=30,
        ),
    )
    async with graphql_client as graphql_session:
        # Root Organisation
        if config.root_organisation is not None:
            logger.info("Handling root organisation")
            await ensure_root_organisation(graphql_session, config.root_organisation)

        # IT Systems
        # NOTE: This MUST come before classes, since they can reference IT-systems
        if config.it_systems is not None:
            await ensure_it_systems(graphql_session, config.it_systems)

        # Facets
        # Even though facets are objects in the database equal to classes, they are
        # hard-coded everywhere. For this reason, OS2mo-init will *always* create this
        # expected set of facets.
        facets = {
            "address_property",
            "association_type",
            "employee_address_type",
            "engagement_job_function",
            "engagement_type",
            "kle_aspect",
            "kle_number",
            "leave_type",
            "manager_address_type",
            "manager_level",
            "manager_type",
            "org_unit_address_type",
            "org_unit_hierarchy",
            "org_unit_level",
            "org_unit_type",
            "primary_type",
            "responsibility",
            "role",
            "time_planning",
            "visibility",
        }
        await ensure_facets(graphql_session, facets)

        # Classes
        if config.facets is not None:
            await ensure_classes(graphql_session, config.facets)
