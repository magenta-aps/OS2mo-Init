# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Iterable
from typing import cast
from typing import Optional
from uuid import UUID

from httpx import AsyncClient
from raclients.modelclient.lora import ModelClient as LoRaModelClient
from raclients.modelclient.mo import ModelClient as MOModelClient
from ramodels.lora import Facet
from ramodels.lora import Organisation
from ramodels.lora.itsystem import ITSystem
from ramodels.mo import FacetClass

from os2mo_init import mo
from os2mo_init.config import ConfigFacet
from os2mo_init.util import generate_uuid


async def ensure_root_organisation(
    lora_model_client: LoRaModelClient,
    name: str,
    user_key: str,
    municipality_code: Optional[int] = None,
    existing_uuid: Optional[UUID] = None,
) -> UUID:
    """
    Idempotently ensure a single root organisation exists with the given parameters.

    Args:
        lora_model_client: LoRa model client.
        name: Root organisation name.
        user_key: Root organisation user key.
        municipality_code: Root organisation municipality code.
        existing_uuid: Optional UUID of the potentially pre-existing root organisation.

    Returns: UUID of the (potentially created or updated) root organisation.
    """
    root_organisation = Organisation.from_simplified_fields(
        uuid=existing_uuid or generate_uuid("organisations.__root__"),
        name=name,
        user_key=user_key,
        municipality_code=municipality_code,
    )
    await lora_model_client.upload([root_organisation])
    return cast(UUID, root_organisation.uuid)


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
    await lora_model_client.upload(facets)
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
    await mo_model_client.upload(classes)
    return classes


async def ensure_it_systems(
    mo_client: AsyncClient,
    lora_model_client: LoRaModelClient,
    organisation_uuid: UUID,
    it_systems_config: dict[str, str],
) -> list[ITSystem]:
    """
    Idempotently ensure the given IT Systems exist in LoRa.

    Args:
        mo_client: Authenticated MO client.
        lora_model_client: LoRa model client.
        organisation_uuid: Root organisation UUID the IT Systems are created under.
        it_systems_config: Dictionary mapping IT System user keys into names.

    Returns: Dictionary of (potentially created or updated) IT systems.
    """
    existing_it_systems = await mo.get_it_systems(
        client=mo_client,
        organisation_uuid=organisation_uuid,
    )
    it_systems = [
        ITSystem.from_simplified_fields(
            uuid=existing_it_systems.get(
                user_key, generate_uuid(f"it_systems.{user_key}")
            ),
            state="Aktiv",
            user_key=user_key,
            name=name,
            from_date="1930-01-01",
            to_date="infinity",
            affiliated_orgs=[organisation_uuid],
        )
        for user_key, name in it_systems_config.items()
    ]
    await lora_model_client.upload(it_systems)
    return it_systems
