# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from typing import cast
from typing import Optional
from uuid import UUID

from gql import gql
from gql.client import AsyncClientSession
from gql.transport.exceptions import TransportQueryError
from httpx import AsyncClient
from ra_utils.asyncio_utils import gather_with_concurrency
from structlog import get_logger

logger = get_logger(__name__)


async def get_root_org(graphql_session: AsyncClientSession) -> Optional[UUID]:
    """
    Get UUID of the existing root MO organisation.

    Args:
        graphql_session: MO GraphQL client session.

    Returns: The UUID of the root organisation if it is configured. None otherwise.
    """
    query = gql(
        """
        query RootOrgQuery {
            org {
                uuid
            }
        }
        """
    )
    try:
        logger.debug("Getting root org UUID from MO...")

        result = await graphql_session.execute(query)
        root_org_uuid = result["org"]["uuid"]

        logger.debug("Root org uuid", uuid=root_org_uuid)

        return UUID(root_org_uuid)
    except TransportQueryError as e:
        logger.debug("Error getting root org UUID from MO", exc=e)
        if (
            e.errors is not None
            and e.errors[0].message == "ErrorCodes.E_ORG_UNCONFIGURED"
        ):
            return None
        raise e


async def get_facets(client: AsyncClient, organisation_uuid: UUID) -> dict[str, UUID]:
    """
    Get existing facets.

    Args:
        client: Authenticated MO client.
        organisation_uuid: Root organisation UUID of the facets.

    Returns: Dictionary mapping facet user keys into their UUIDs.
    """
    r = await client.get(f"/service/o/{organisation_uuid}/f/")
    r.raise_for_status()
    facets = r.json()
    return {f["user_key"]: UUID(f["uuid"]) for f in facets}


async def get_classes_for_facet(
    client: AsyncClient, facet_uuid: UUID
) -> list[dict[str, Any]]:
    """
    Get existing classes for a given facet.

    Args:
        client: Authenticated MO client.
        facet_uuid: UUID of the facet to get classes for.

    Returns: List of class dicts for the given facet.
    """
    r = await client.get(f"/service/f/{facet_uuid}/")
    r.raise_for_status()
    return cast(list[dict[str, Any]], r.json()["data"]["items"])


async def get_classes(
    client: AsyncClient, facets: dict[str, UUID]
) -> dict[str, dict[str, UUID]]:
    """
    Get existing classes.

    Args:
        client: Authenticated MO client.
        facets: Dictionary mapping facet user keys into UUIDs.

    Returns: Nested dictionary mapping facet user keys to a dictionary mapping class
     user keys to UUIDs.
    """
    classes_for_facets = (
        get_classes_for_facet(client=client, facet_uuid=facet_uuid)
        for facet_uuid in facets.values()
    )
    facets_and_classes = zip(
        facets.keys(), await gather_with_concurrency(5, *classes_for_facets)
    )
    return {
        facet_user_key: {
            facet_class["user_key"]: UUID(facet_class["uuid"])
            for facet_class in facet_classes
        }
        for facet_user_key, facet_classes in facets_and_classes
    }


async def get_it_systems(
    client: AsyncClient, organisation_uuid: UUID
) -> dict[str, UUID]:
    """
    Get existing IT Systems.

    Args:
        client: Authenticated MO client.
        organisation_uuid: Root organisation UUID of the IT Systems.

    Returns: Dictionary mapping IT System user keys into their UUIDs.
    """
    r = await client.get(f"/service/o/{organisation_uuid}/it/")
    r.raise_for_status()
    it_systems = r.json()
    return {i["user_key"]: UUID(i["uuid"]) for i in it_systems}
