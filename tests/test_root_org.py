# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import ANY
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from gql.transport.exceptions import TransportQueryError
from graphql import GraphQLError

from os2mo_init.config import ConfigRootOrganisation
from os2mo_init.root_org import ensure_root_organisation
from os2mo_init.root_org import get_root_org
from os2mo_init.root_org import RootOrg


async def test_get_root_org() -> None:
    """Test GraphQL parsing."""
    graphql_session = AsyncMock()
    graphql_session.execute.return_value = {
        "org": {
            "uuid": "67bae43a-2b92-484a-9476-95135633aaf4",
            "municipality_code": 123,
        }
    }
    root_org = await get_root_org(graphql_session)
    assert root_org is not None
    assert root_org.uuid == UUID("67bae43a-2b92-484a-9476-95135633aaf4")
    assert root_org.municipality_code == 123


async def test_get_root_org_unconfigured() -> None:
    """Test that the OS2mo error is caught."""
    graphql_session = AsyncMock()
    graphql_session.execute.side_effect = TransportQueryError(
        "Boom!",
        errors=[
            GraphQLError("ErrorCodes.E_ORG_UNCONFIGURED"),
        ],
    )
    root_org = await get_root_org(graphql_session)
    assert root_org is None


async def test_ensure_root_organisation_create(monkeypatch) -> None:
    """Test that the root organisation is created."""
    get_root_org_mock = AsyncMock()
    get_root_org_mock.return_value = None
    monkeypatch.setattr("os2mo_init.root_org.get_root_org", get_root_org_mock)

    graphql_session = AsyncMock()
    config_root_organisation = ConfigRootOrganisation(
        municipality_code=123,
    )

    await ensure_root_organisation(graphql_session, config_root_organisation)

    graphql_session.execute.assert_awaited_once_with(ANY, {"municipality_code": 123})


async def test_ensure_root_organisation_no_change(monkeypatch) -> None:
    """Test that nothing is uploaded if no changes."""
    get_root_org_mock = AsyncMock()
    get_root_org_mock.return_value = RootOrg(
        uuid=UUID("67bae43a-2b92-484a-9476-95135633aaf4"),
        municipality_code=123,
    )
    monkeypatch.setattr("os2mo_init.root_org.get_root_org", get_root_org_mock)

    graphql_session = AsyncMock()
    config_root_organisation = ConfigRootOrganisation(
        municipality_code=123,
    )

    await ensure_root_organisation(graphql_session, config_root_organisation)

    graphql_session.execute.assert_not_awaited()


async def test_ensure_root_organisation_municipality_change(monkeypatch) -> None:
    """Test that an error is thrown if attempting to change municipality code."""
    get_root_org_mock = AsyncMock()
    get_root_org_mock.return_value = RootOrg(
        uuid=UUID("67bae43a-2b92-484a-9476-95135633aaf4"),
        municipality_code=111,
    )
    monkeypatch.setattr("os2mo_init.root_org.get_root_org", get_root_org_mock)

    graphql_session = AsyncMock()
    config_root_organisation = ConfigRootOrganisation(
        municipality_code=222,
    )

    with pytest.raises(NotImplementedError):
        await ensure_root_organisation(graphql_session, config_root_organisation)
