# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from gql import gql
from gql.client import AsyncClientSession
from pydantic import BaseModel
from pydantic import parse_obj_as
from structlog import get_logger

from os2mo_init.config import ConfigFacet
from os2mo_init.it_systems import get_it_systems

logger = get_logger(__name__)


class ITSystem(BaseModel):
    uuid: UUID


class Class(BaseModel):
    uuid: UUID
    user_key: str
    name: str
    scope: str | None
    it_system: ITSystem | None

    @property
    def it_system_uuid(self) -> UUID | None:
        return getattr(self.it_system, "uuid", None)


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
                  it_system {
                    uuid
                  }
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
    existing_classes_by_user_key: dict[str, dict[str, Class]] = {
        f.user_key: {c.user_key: c for c in f.classes} for f in existing_classes
    }
    existing_it_systems_by_user_key = await get_it_systems(graphql_session)

    create_mutation = gql(
        """
        mutation CreateClassMutation(
          $facet_uuid: UUID!,
          $user_key: String!
          $name: String!,
          $scope: String!,
          $it_system_uuid: UUID,
        ) {
          class_create(
            input: {
              facet_uuid: $facet_uuid,
              user_key: $user_key,
              name: $name,
              scope: $scope,
              it_system_uuid: $it_system_uuid,
              validity: {
                from: null,
              }
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
          $scope: String!,
          $it_system_uuid: UUID,
        ) {
          class_update(
            input: {
              uuid: $uuid
              facet_uuid: $facet_uuid,
              user_key: $user_key
              name: $name,
              scope: $scope,
              it_system_uuid: $it_system_uuid,
              validity: {
                from: null,
              }
            }
          ) {
            uuid
          }
        }
    """
    )

    for facet_user_key, classes in config_classes.items():
        for class_user_key, class_data in classes.items():
            it_system_uuid = None
            if class_data.it_system is not None:
                try:
                    it_system = existing_it_systems_by_user_key[class_data.it_system]
                except KeyError as e:
                    raise ValueError(
                        # noqa: E501
                        f"Class '{class_user_key}' cannot be associated with non-existent it-system '{class_data.it_system}'"
                    ) from e
                it_system_uuid = str(it_system.uuid)
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
                        "it_system_uuid": it_system_uuid,
                    },
                )
                continue
            if (
                existing.name != class_data.title
                or existing.scope != class_data.scope
                or existing.it_system_uuid != class_data.it_system
            ):
                logger.info("Updating class", data=class_data)
                await graphql_session.execute(
                    update_mutation,
                    {
                        "facet_uuid": str(facet_uuids[facet_user_key]),
                        "uuid": str(existing.uuid),
                        "user_key": class_user_key,
                        "name": class_data.title,
                        "scope": class_data.scope,
                        "it_system_uuid": it_system_uuid,
                    },
                )
