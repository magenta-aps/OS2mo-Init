# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
from contextlib import asynccontextmanager
from contextlib import AsyncExitStack
from dataclasses import dataclass
from typing import AsyncIterator

from gql.client import AsyncClientSession
from httpx import AsyncClient
from pydantic import AnyHttpUrl
from raclients.auth import AuthenticatedAsyncHTTPXClient
from raclients.graph.client import GraphQLClient
from raclients.modelclient.lora import ModelClient as LoRaModelClient
from raclients.modelclient.mo import ModelClient as MoModelClient
from structlog import get_logger

logger = get_logger(__name__)


@dataclass
class Clients:
    mo_graphql_session: AsyncClientSession
    mo_client: AsyncClient
    lora_client: AsyncClient
    mo_model_client: MoModelClient
    lora_model_client: LoRaModelClient


@asynccontextmanager
async def get_clients(
    auth_server: AnyHttpUrl,
    mo_url: AnyHttpUrl,
    client_id: str,
    client_secret: str,
    auth_realm: str,
    lora_url: AnyHttpUrl,
) -> AsyncIterator[Clients]:
    """
    Get GraphQL, HTTP, and Model Clients.

    Args:
        auth_server: Keycloak authentication server.
        mo_url: OS2mo URL.
        client_id: Client ID used to authenticate against OS2mo.
        client_secret: Client secret used to authenticate against OS2mo.
        auth_realm: Keycloak realm for OS2mo authentication.
        lora_url: LoRa URL.

    Yields: Clients object containing opened clients.
    """

    logger.debug("Getting GraphQL, HTTP and Model clients...")

    mo_auth_settings = dict(
        client_id=client_id,
        client_secret=client_secret,
        auth_realm=auth_realm,
        auth_server=auth_server,
    )

    mo_graphql_client = GraphQLClient(
        url=f"{mo_url}/graphql/v2",
        **mo_auth_settings,
    )

    mo_client = AuthenticatedAsyncHTTPXClient(
        base_url=mo_url,
        **mo_auth_settings,
    )
    lora_client = AsyncClient(
        base_url=lora_url,
    )

    mo_model_client = MoModelClient(
        base_url=mo_url,
        **mo_auth_settings,
    )
    lora_model_client = LoRaModelClient(
        base_url=lora_url,
    )

    async with AsyncExitStack() as stack:
        contexts = await asyncio.gather(
            stack.enter_async_context(mo_graphql_client),
            stack.enter_async_context(mo_client),
            stack.enter_async_context(lora_client),
            stack.enter_async_context(mo_model_client),
            stack.enter_async_context(lora_model_client),
        )
        mo_graphql_session, mo_client_session, lora_client_session, *_ = contexts
        yield Clients(
            mo_graphql_session=mo_graphql_session,
            mo_client=mo_client_session,
            lora_client=lora_client_session,
            mo_model_client=mo_model_client,
            lora_model_client=lora_model_client,
        )
