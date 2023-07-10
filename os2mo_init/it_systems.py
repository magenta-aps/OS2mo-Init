# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from gql import gql
from gql.client import AsyncClientSession
from pydantic import BaseModel
from pydantic import parse_obj_as
from structlog import get_logger

logger = get_logger(__name__)


class ITSystem(BaseModel):
    uuid: UUID
    user_key: str
    name: str


async def get_it_systems(graphql_session: AsyncClientSession) -> dict[str, ITSystem]:
    """
    Get all IT Systems in OS2mo.

    Args:
        graphql_session: MO GraphQL client session.

    Returns:
        Dictionary mapping IT System user keys to ITSystem objects.
    """
    logger.info("Getting IT systems")
    query = gql(
        """
        query ITSystemsQuery {
          itsystems {
            objects {
              current {
                uuid
                user_key
                name
              }
            }
          }
        }
    """
    )
    result = await graphql_session.execute(query)
    it_system_list = parse_obj_as(
        list[ITSystem], [s["current"] for s in result["itsystems"]["objects"]]
    )
    return {s.user_key: s for s in it_system_list}


async def ensure_it_systems(
    graphql_session: AsyncClientSession,
    config_it_systems: dict[str, str],
) -> None:
    """Ensure that the given IT Systems exists.

    Args:
        graphql_session: MO GraphQL client session.
        config_it_systems: Dictionary mapping from desired IT System user key to name.
    """
    logger.info("Ensuring IT Systems", it_systems=config_it_systems)

    existing_it_systems = await get_it_systems(graphql_session)
    logger.debug("Existing IT Systems", existing=existing_it_systems)

    create_mutation = gql(
        """
        mutation CreateITSystemMutation($user_key: String!, $name: String!) {
          itsystem_create(input: {user_key: $user_key, name: $name}) {
            uuid
          }
        }
        """
    )
    update_mutation = gql(
        """
        mutation UpdateITSystemMutation(
          $uuid: UUID!,
          $user_key: String!,
          $name: String!
        ) {
          itsystem_update(uuid: $uuid, input: {user_key: $user_key, name: $name}) {
            uuid
          }
        }
        """
    )

    for user_key, name in config_it_systems.items():
        try:
            existing = existing_it_systems[user_key]
        except KeyError:
            logger.info("Creating IT System", user_key=user_key)
            await graphql_session.execute(
                create_mutation,
                {
                    "user_key": user_key,
                    "name": name,
                },
            )
            continue
        if existing.name != name:
            logger.info("Updating IT System", user_key=user_key)
            await graphql_session.execute(
                update_mutation,
                {
                    "uuid": str(existing.uuid),
                    "user_key": user_key,
                    "name": name,
                },
            )
