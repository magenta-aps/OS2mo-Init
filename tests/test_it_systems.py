# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import ANY
from unittest.mock import AsyncMock
from unittest.mock import call
from uuid import UUID

from os2mo_init.it_systems import ensure_it_systems
from os2mo_init.it_systems import get_it_systems
from os2mo_init.it_systems import ITSystem


async def test_get_it_systems() -> None:
    """Test GraphQL parsing."""
    graphql_session = AsyncMock()
    graphql_session.execute.return_value = {
        "itsystems": {
            "objects": [
                {
                    "current": {
                        "uuid": "49d91308-67b0-4b8c-b787-1cd58e3039bd",
                        "user_key": "OS2MO",
                        "name": "mo",
                    }
                },
                {
                    "current": {
                        "uuid": "5168dd45-4cb5-4932-b8a1-10dbe736fc5d",
                        "user_key": "NextCloud",
                        "name": "NextCloud",
                    }
                },
            ]
        }
    }

    it_systems = await get_it_systems(graphql_session)

    assert it_systems == {
        "OS2MO": ITSystem(
            uuid=UUID("49d91308-67b0-4b8c-b787-1cd58e3039bd"),
            user_key="OS2MO",
            name="mo",
        ),
        "NextCloud": ITSystem(
            uuid=UUID("5168dd45-4cb5-4932-b8a1-10dbe736fc5d"),
            user_key="NextCloud",
            name="NextCloud",
        ),
    }


async def test_ensure_it_systems(monkeypatch) -> None:
    """Test that IT Systems are created or updated."""
    get_it_systems_mock = AsyncMock()
    get_it_systems_mock.return_value = {
        "OS2MO": ITSystem(
            uuid=UUID("49d91308-67b0-4b8c-b787-1cd58e3039bd"),
            user_key="OS2MO",
            name="mo",
        ),
    }
    monkeypatch.setattr("os2mo_init.it_systems.get_it_systems", get_it_systems_mock)

    graphql_session = AsyncMock()

    config_it_systems = {
        "OS2MO": "os2mo",
        "NEXTCLOUD": "NextCloud",
    }
    await ensure_it_systems(graphql_session, config_it_systems)

    graphql_session.execute.assert_has_awaits(
        [
            call(
                ANY,
                {
                    "uuid": "49d91308-67b0-4b8c-b787-1cd58e3039bd",
                    "user_key": "OS2MO",
                    "name": "os2mo",
                },
            ),
            call(
                ANY,
                {
                    "user_key": "NEXTCLOUD",
                    "name": "NextCloud",
                },
            ),
        ]
    )
