# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from gql import gql
from gql.client import AsyncClientSession
from gql.transport.exceptions import TransportQueryError
from more_itertools import one
from pydantic import BaseModel
from structlog import get_logger

from os2mo_init.config import ConfigRootOrganisation

logger = get_logger(__name__)


class RootOrg(BaseModel):
    uuid: UUID
    municipality_code: int | None


async def get_root_org(graphql_session: AsyncClientSession) -> RootOrg | None:
    logger.debug("Getting root org from MO")
    query = gql(
        """
        query RootOrgQuery {
            org {
                uuid
                municipality_code
            }
        }
        """
    )
    try:
        result = await graphql_session.execute(query)
    except TransportQueryError as e:
        logger.debug("Error getting root org from MO", exc=e)
        if (
            e.errors is not None
            and one(e.errors).message == "ErrorCodes.E_ORG_UNCONFIGURED"
        ):
            return None
        raise
    return RootOrg.parse_obj(result["org"])


async def ensure_root_organisation(
    graphql_session: AsyncClientSession,
    config_root_organisation: ConfigRootOrganisation,
) -> None:
    """
    Ensure that the root organisation exists with the given configuration.

    Args:
        graphql_session: MO GraphQL client session.
        config_root_organisation: Desired root organisation.
    """
    logger.info("Ensuring root org", root_org=config_root_organisation)
    root_org = await get_root_org(graphql_session)
    logger.debug("Existing root org", existing=root_org)
    if root_org is not None:
        if root_org.municipality_code != config_root_organisation.municipality_code:
            raise NotImplementedError(
                "Changing municipality code is not implemented in OS2mo."
            )
        logger.info("Root org already configured")
        return

    logger.info("Creating org org")
    mutation = gql(
        """
        mutation RootOrgCreate($municipality_code: Int) {
          org_create(input: {municipality_code: $municipality_code}) {
            uuid
          }
        }
        """
    )
    await graphql_session.execute(
        mutation,
        {"municipality_code": config_root_organisation.municipality_code},
    )
