# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from gql import gql
from gql.client import AsyncClientSession
from structlog import get_logger

logger = get_logger(__name__)


async def get_facets(graphql_session: AsyncClientSession) -> set[str]:
    """
    Get all facets in OS2mo.

    Args:
        graphql_session: MO GraphQL client session.

    Returns:
        Set of facet user keys.
    """
    logger.info("Getting facets")
    query = gql(
        """
        query FacetsQuery {
          facets {
            objects {
              current {
                user_key
              }
            }
          }
        }
        """
    )
    result = await graphql_session.execute(query)
    return {f["current"]["user_key"] for f in result["facets"]["objects"]}


async def ensure_facets(
    graphql_session: AsyncClientSession,
    config_facets: set[str],
) -> None:
    """
    Ensure that the given facets exists.

    Args:
        graphql_session: MO GraphQL client session.
        config_facets: Desired facets.
    """
    logger.info("Ensuring facets", facets=config_facets)

    existing_facets = await get_facets(graphql_session)
    logger.debug("Existing facets", existing=existing_facets)

    missing_facets = config_facets - existing_facets

    mutation = gql(
        """
        mutation CreateFacetMutation($user_key: String!) {
          facet_create(input: {user_key: $user_key}) {
            uuid
          }
        }
        """
    )
    for user_key in missing_facets:
        logger.info("Creating facet", user_key=user_key)
        await graphql_session.execute(
            mutation,
            {"user_key": user_key},
        )
