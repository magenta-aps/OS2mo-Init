# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from gql.transport.exceptions import TransportQueryError
from graphql import GraphQLError
from httpx import AsyncClient
from ramodels.mo import FacetClass

from os2mo_init import mo


@pytest.mark.asyncio
async def test_get_root_org(root_org_uuid: UUID) -> None:
    graphql_session_mock = AsyncMock()
    graphql_session_mock.execute.return_value = {"org": {"uuid": str(root_org_uuid)}}
    assert await mo.get_root_org(graphql_session=graphql_session_mock) == root_org_uuid


@pytest.mark.asyncio
async def test_get_unconfigured_root_org() -> None:
    graphql_session_mock = AsyncMock()
    graphql_session_mock.execute.side_effect = TransportQueryError(
        "error!",
        errors=[GraphQLError(message="ErrorCodes.E_ORG_UNCONFIGURED")],
    )
    assert await mo.get_root_org(graphql_session=graphql_session_mock) is None


@pytest.mark.asyncio
async def test_get_root_org_exception() -> None:
    graphql_session_mock = AsyncMock()
    graphql_session_mock.execute.side_effect = AssertionError()
    with pytest.raises(AssertionError):
        await mo.get_root_org(graphql_session=graphql_session_mock)


@pytest.mark.asyncio
async def test_get_facets(
    async_client: AsyncClient, facets_mock: dict[str, UUID], root_org_uuid: UUID
) -> None:
    actual = await mo.get_facets(
        client=async_client,
        organisation_uuid=root_org_uuid,
    )
    assert actual == facets_mock


@pytest.mark.asyncio
async def test_get_classes_for_facet(
    async_client: AsyncClient,
    facets: dict[str, UUID],
    classes_mock: dict[str, dict[str, dict[str, str]]],
) -> None:
    actual = await mo.get_classes_for_facet(
        client=async_client,
        facet_uuid=facets["org_unit_address_type"],
    )
    assert actual == list(classes_mock["org_unit_address_type"].values())


@pytest.mark.asyncio
async def test_get_classes(
    async_client: AsyncClient,
    facets: dict[str, UUID],
    classes_mock: dict[str, dict[str, dict[str, str]]],
) -> None:
    actual = await mo.get_classes(
        client=async_client,
        facets=facets,
    )
    expected = {
        facet_user_key: {
            class_user_key: UUID(klass["uuid"])
            for class_user_key, klass in facet_classes.items()
        }
        for facet_user_key, facet_classes in classes_mock.items()
    }
    assert actual == expected
