# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from gql import gql
from gql.client import AsyncClientSession
from pydantic import BaseModel
from pydantic import parse_obj_as
from structlog import get_logger

from os2mo_init.config import ConfigFacet

logger = get_logger(__name__)


class Class(BaseModel):
    uuid: UUID
    user_key: str
    name: str
    scope: str | None


class Facet(BaseModel):
    uuid: UUID
    user_key: str
    classes: list[Class]


async def get_classes(graphql_session: AsyncClientSession) -> list[Facet]:
    """
    Get all classes in OS2mo.

    Args:
        graphql_session: MO GraphQL client session.

    Returns:
        List of Facets, which contain Classes.
    """
    logger.info("Getting classes")
    query = gql(
        """
        query ClassesQuery {
          facets {
            objects {
              current {
                uuid
                user_key
                classes {
                  uuid
                  user_key
                  name
                  scope
                }
              }
            }
          }
        }
    """
    )
    result = await graphql_session.execute(query)
    return parse_obj_as(
        list[Facet], [f["current"] for f in result["facets"]["objects"]]
    )


async def ensure_classes(
    graphql_session: AsyncClientSession,
    config_classes: dict[str, ConfigFacet],
) -> None:
    """Ensure that the given classes exists.

    Args:
        graphql_session: MO GraphQL client session.
        config_classes: Desired facets and their classes.
    """
    logger.info("Ensuring classes", classes=config_classes)

    existing_classes = await get_classes(graphql_session)
    logger.debug("Existing classes", existing=existing_classes)
    facet_uuids = {f.user_key: f.uuid for f in existing_classes}
    existing_classes_by_user_key = {
        f.user_key: {c.user_key: c for c in f.classes} for f in existing_classes
    }

    create_mutation = gql(
        """
        mutation CreateClassMutation(
          $facet_uuid: UUID!,
          $user_key: String!
          $name: String!,
          $scope: String!,
        ) {
          class_create(
            input: {
              facet_uuid: $facet_uuid,
              user_key: $user_key,
              name: $name,
              scope: $scope,
            }
          ) {
            uuid
          }
        }
        """
    )
    update_mutation = gql(
        """
        mutation UpdateClassMutation(
          $facet_uuid: UUID!,
          $uuid: UUID!,
          $user_key: String!,
          $name: String!,
          $scope: String!
        ) {
          class_update(
            uuid: $uuid
            input: {
              facet_uuid: $facet_uuid,
              user_key: $user_key
              name: $name,
              scope: $scope,
            }
          ) {
            uuid
          }
        }
    """
    )

    for facet_user_key, classes in config_classes.items():
        for class_user_key, class_data in classes.items():
            try:
                existing = existing_classes_by_user_key[facet_user_key][class_user_key]
            except KeyError:
                logger.info("Creating class", data=class_data)
                await graphql_session.execute(
                    create_mutation,
                    {
                        "facet_uuid": str(facet_uuids[facet_user_key]),
                        "user_key": class_user_key,
                        "name": class_data.title,
                        "scope": class_data.scope,
                    },
                )
                continue
            if existing.name != class_data.title or existing.scope != class_data.scope:
                logger.info("Updating class", data=class_data)
                await graphql_session.execute(
                    update_mutation,
                    {
                        "facet_uuid": str(facet_uuids[facet_user_key]),
                        "uuid": str(existing.uuid),
                        "user_key": class_user_key,
                        "name": class_data.title,
                        "scope": class_data.scope,
                    },
                )
