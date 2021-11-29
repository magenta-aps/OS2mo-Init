# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from io import TextIOWrapper

import click
from pydantic import AnyHttpUrl
from ra_utils.async_to_sync import async_to_sync

from os2mo_init import initialisers
from os2mo_init.clients import get_clients
from os2mo_init.config import get_config
from os2mo_init.util import validate_url


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
    "--lora-url",
    help="LoRa URL.",
    required=True,
    callback=validate_url,
    envvar="LORA_URL",
    show_envvar=True,
)
@click.option(
    "--lora-client-id",
    help="Client ID used to authenticate against LoRa.",
    required=True,
    default="dipex",
    envvar="LORA_CLIENT_ID",
    show_envvar=True,
)
@click.option(
    "--lora-client-secret",
    help="Client secret used to authenticate against LoRa.",
    required=True,
    envvar="LORA_CLIENT_SECRET",
    show_envvar=True,
)
@click.option(
    "--lora-auth-realm",
    help="Keycloak realm for LoRa authentication.",
    required=True,
    default="lora",
    envvar="LORA_AUTH_REALM",
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
@async_to_sync
async def run(
    auth_server: AnyHttpUrl,
    mo_url: AnyHttpUrl,
    client_id: str,
    client_secret: str,
    auth_realm: str,
    lora_url: AnyHttpUrl,
    lora_client_id: str,
    lora_client_secret: str,
    lora_auth_realm: str,
    config_file: TextIOWrapper,
) -> None:
    config = get_config(config_file)
    async with get_clients(
        auth_server=auth_server,
        mo_url=mo_url,
        client_id=client_id,
        client_secret=client_secret,
        auth_realm=auth_realm,
        lora_url=lora_url,
        lora_client_id=lora_client_id,
        lora_client_secret=lora_client_secret,
        lora_auth_realm=lora_auth_realm,
    ) as clients:
        # LoRa setup
        root_organisation_uuid = await initialisers.ensure_root_organisation(
            mo_graphql_session=clients.mo_graphql_session,
            lora_model_client=clients.lora_model_client,
            **config.root_organisation.dict(),
        )

        facet_user_keys = config.facets.keys()
        facets = await initialisers.ensure_facets(
            mo_client=clients.mo_client,
            lora_model_client=clients.lora_model_client,
            organisation_uuid=root_organisation_uuid,
            user_keys=facet_user_keys,
        )
        facet_uuids = dict(zip(facet_user_keys, (f.uuid for f in facets)))

        await initialisers.ensure_it_systems(
            mo_client=clients.mo_client,
            lora_client=clients.lora_client,
            organisation_uuid=root_organisation_uuid,
            it_systems_config=config.it_systems,
        )

        # MO setup
        await initialisers.ensure_classes(
            mo_client=clients.mo_client,
            mo_model_client=clients.mo_model_client,
            organisation_uuid=root_organisation_uuid,
            facet_classes_config=config.facets,
            facet_uuids=facet_uuids,
        )
