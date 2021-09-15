# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
from collections import Callable
from typing import List
from uuid import UUID

from ra_utils.generate_uuid import uuid_generator
from raclients.lora import ModelClient as LoRaModelClient
from ramodels.lora import Facet
from ramodels.lora import Klasse
from ramodels.lora import Organisation

from . import defaults


async def ensure_root_organisation(
    client: LoRaModelClient,
    name: str,
    municipality_code: int = None,
    generate_uuid: Callable[[str], UUID] = uuid_generator(base=__package__),
) -> UUID:
    response = await client.load_lora_objs(
        [
            Organisation.from_simplified_fields(
                uuid=generate_uuid(""),
                name=name,
                user_key=name,
                municipality_code=municipality_code,
            )
        ]
    )
    return UUID(response[0]["uuid"])


async def ensure_default_facets(
    client: LoRaModelClient,
    organisation_uuid: UUID,
    generate_uuid: Callable[[str], UUID] = uuid_generator(base=__package__),
) -> List[UUID]:
    response = await client.load_lora_objs(
        Facet.from_simplified_fields(
            uuid=generate_uuid(user_key),
            user_key=user_key,
            organisation_uuid=organisation_uuid,
        )
        for user_key in defaults.facets
    )
    return [UUID(r["uuid"]) for r in response]


async def ensure_default_classes(
    client: LoRaModelClient,
    organisation_uuid: UUID,
    generate_uuid: Callable[[str], UUID] = uuid_generator(base=__package__),
) -> List[UUID]:
    response = await client.load_lora_objs(
        Klasse.from_simplified_fields(
            facet_uuid=generate_uuid(facet),
            uuid=generate_uuid(user_key),
            user_key=user_key,
            organisation_uuid=organisation_uuid,
            title=fields["title"],
            scope=fields["scope"],
        )
        for facet, facet_classes in defaults.classes.items()
        for user_key, fields in facet_classes.items()
    )
    return [UUID(r["uuid"]) for r in response]
