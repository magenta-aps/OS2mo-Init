# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections import defaultdict
from uuid import UUID

import pytest
from httpx import AsyncClient
from respx import MockRouter

from os2mo_init.util import generate_uuid


@pytest.fixture
def root_org_uuid() -> UUID:
    return UUID("6c3a0f88-743a-47fc-a836-e5eed7d0ef93")


@pytest.fixture
def async_client() -> AsyncClient:
    return AsyncClient(base_url="https://mo")


@pytest.fixture
def facets() -> dict[str, UUID]:
    return {
        "org_unit_address_type": UUID("1859dc13-93ec-8319-33bf-348a857c2f9b"),
        "leave_type": UUID("225f580e-30b3-4ef1-9c98-3aa180258d25"),
    }


@pytest.fixture
def facets_mock(
    async_client: AsyncClient,
    root_org_uuid: UUID,
    facets: dict[str, UUID],
    respx_mock: MockRouter,
) -> dict[str, UUID]:
    respx_mock.get(f"{async_client.base_url}/service/o/{root_org_uuid}/f/").respond(
        json=[
            {
                "uuid": str(facet_uuid),
                "user_key": facet_user_key,
            }
            for facet_user_key, facet_uuid in facets.items()
        ]
    )
    return facets


@pytest.fixture
def classes() -> dict[str, dict[str, dict[str, str]]]:
    return {
        "org_unit_address_type": {
            "PhoneUnit": {
                "uuid": "251df3af-045a-97f7-484d-1534b19e8dda",
                "user_key": "PhoneUnit",
                "name": "Telefon",
                "scope": "EMAIL",
            }
        },
        "leave_type": {
            "Orlov": {
                "uuid": "391bb2ba-9452-44a3-ad65-e19d3df1ae62",
                "user_key": "Orlov",
                "name": "Orlov",
                "scope": "TEXT",
            },
        },
    }


@pytest.fixture
def classes_mock(
    async_client: AsyncClient,
    facets: dict[str, UUID],
    classes: dict[str, dict[str, dict[str, str]]],
    respx_mock: MockRouter,
) -> dict[str, dict[str, dict[str, str]]]:
    for facet_user_key, facet_classes in classes.items():
        respx_mock.get(
            url=f"{async_client.base_url}/service/f/{facets[facet_user_key]}/"
        ).respond(
            json={
                "data": {
                    "items": list(facet_classes.values()),
                }
            }
        )
    return classes
