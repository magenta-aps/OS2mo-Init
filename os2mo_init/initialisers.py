# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Iterable
from typing import Optional
from uuid import UUID

from gql.client import AsyncClientSession
from httpx import AsyncClient
from raclients.lora import ModelClient as LoRaModelClient
from raclients.mo import ModelClient as MOModelClient
from ramodels.lora import Facet
from ramodels.lora import Organisation
from ramodels.mo import FacetClass

from os2mo_init import mo
from os2mo_init.config import ConfigFacet
from os2mo_init.util import generate_uuid


async def ensure_root_organisation(
    mo_graphql_session: AsyncClientSession,
    lora_model_client: LoRaModelClient,
    name: str,
    user_key: str,
    municipality_code: Optional[int] = None,
) -> UUID:
    """
    Idempotently ensure a single root organisation exists with the given parameters.

    Args:
        mo_graphql_session: MO GraphQL client session.
        lora_model_client: LoRa model client.
        name: Root organisation name.
        user_key: Root organisation user key.
        municipality_code: Root organisation municipality code.

    Returns: UUID of the (potentially created or updated) root organisation.
    """
    existing_uuid = await mo.get_root_org(mo_graphql_session)
    root_organisation = Organisation.from_simplified_fields(
        uuid=existing_uuid or generate_uuid("organisations.__root__"),
        name=name,
        user_key=user_key,
        municipality_code=municipality_code,
    )
    await lora_model_client.load_lora_objs([root_organisation])
    return root_organisation.uuid


async def ensure_facets(
    mo_client: AsyncClient,
    lora_model_client: LoRaModelClient,
    organisation_uuid: UUID,
    user_keys: Iterable[str],
) -> list[Facet]:
    """
    Idempotently ensure the given facets exist.

    Args:
        mo_client: Authenticated MO client.
        lora_model_client: LoRa model client.
        organisation_uuid: Root organisation UUID the facets are created under.
        user_keys: Facet user keys to ensure exist.

    Returns: List of (potentially created or updated) facet objects.
    """
    existing_facets = await mo.get_facets(
        client=mo_client,
        organisation_uuid=organisation_uuid,
    )
    facets = [
        Facet.from_simplified_fields(
            uuid=existing_facets.get(user_key, generate_uuid(f"facets.{user_key}")),
            user_key=user_key,
            organisation_uuid=organisation_uuid,
        )
        for user_key in user_keys
    ]
    await lora_model_client.load_lora_objs(facets)
    return facets


async def ensure_classes(
    mo_client: AsyncClient,
    mo_model_client: MOModelClient,
    organisation_uuid: UUID,
    facet_classes_config: dict[str, ConfigFacet],
    facet_uuids: dict[str, UUID],
) -> list[FacetClass]:
    """
    Idempotently ensure the given classes exist.

    Args:
        mo_client: Authenticated MO client.
        mo_model_client: MO model client.
        organisation_uuid: Root organisation UUID the classes are created under.
        facet_classes_config: Dictionary mapping facet user keys into ConfigFacets.
        facet_uuids: Dictionary mapping facet user keys into UUIDs.

    Returns: List of (potentially created or updated) facet objects.
    """
    existing_classes = await mo.get_classes(client=mo_client, facets=facet_uuids)
    classes = [
        FacetClass(
            uuid=existing_classes[facet_user_key].get(
                class_user_key,
                generate_uuid(f"facets.{facet_user_key}.classes.{class_user_key}"),
            ),
            facet_uuid=facet_uuids[facet_user_key],
            name=klass.title,
            user_key=class_user_key,
            scope=klass.scope,
            org_uuid=organisation_uuid,
        )
        for facet_user_key, facet in facet_classes_config.items()
        for class_user_key, klass in facet.items()
    ]
    await mo_model_client.load_mo_objs(classes)
    return classes


async def ensure_it_systems() -> None:
    """
    TODO: Migrate from os2mint-omada
    """
    raise NotImplemented()
