# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import ANY
from unittest.mock import AsyncMock

from os2mo_init.facets import ensure_facets
from os2mo_init.facets import get_facets


async def test_get_facets() -> None:
    """Test GraphQL parsing."""
    graphql_session = AsyncMock()
    graphql_session.execute.return_value = {
        "facets": {
            "objects": [
                {
                    "current": {
                        "user_key": "foo",
                    }
                },
                {
                    "current": {
                        "user_key": "bar",
                    }
                },
            ]
        }
    }

    facets = await get_facets(graphql_session)

    assert facets == {"foo", "bar"}


async def test_ensure_facets(monkeypatch) -> None:
    """Test that facets are created."""
    get_facets_mock = AsyncMock()
    get_facets_mock.return_value = {"foo", "bar"}
    monkeypatch.setattr("os2mo_init.facets.get_facets", get_facets_mock)

    graphql_session = AsyncMock()
    config_facets = {"baz"}
    await ensure_facets(graphql_session, config_facets)

    graphql_session.execute.assert_awaited_with(ANY, {"user_key": "baz"})
