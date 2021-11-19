import asyncio
from contextlib import asynccontextmanager
from contextlib import AsyncExitStack
from dataclasses import dataclass

from gql.client import AsyncClientSession
from httpx import AsyncClient
from pydantic import AnyHttpUrl
from ra_utils.headers import TokenSettings
from raclients.auth import AuthenticatedAsyncHTTPXClient
from raclients.graph.client import GraphQLClient
from raclients.lora import ModelClient as LoRaModelClient
from raclients.mo import ModelClient as MoModelClient
from raclients.modelclientbase import common_session_factory


@dataclass
class Clients:
    mo_graphql_session: AsyncClientSession
    mo_client: AsyncClient
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
    lora_client_id: str,
    lora_client_secret: str,
    lora_auth_realm: str,
):
    """
    Get GraphQL, HTTP, and Model Clients.

    Args:
        auth_server: Keycloak authentication server.
        mo_url: OS2mo URL.
        client_id: Client ID used to authenticate against OS2mo.
        client_secret: Client secret used to authenticate against OS2mo.
        auth_realm: Keycloak realm for OS2mo authentication.
        lora_url: LoRa URL.
        lora_client_id: Client ID used to authenticate against LoRa.
        lora_client_secret: Client secret used to authenticate against LoRa.
        lora_auth_realm: Keycloak realm for LoRa authentication.

    Yields: Clients object containing opened clients.
    """
    mo_auth_settings = dict(
        client_id=client_id,
        client_secret=client_secret,
        auth_realm=auth_realm,
        auth_server=auth_server,
    )

    mo_graphql_client = GraphQLClient(
        url=f"{mo_url}/graphql",
        **mo_auth_settings,
    )

    mo_client = AuthenticatedAsyncHTTPXClient(
        base_url=mo_url,
        **mo_auth_settings,
    )

    mo_model_client = MoModelClient(
        base_url=mo_url,
        session_factory=common_session_factory(
            token_settings=TokenSettings(**mo_auth_settings)
        ),
    )

    lora_model_client = LoRaModelClient(
        base_url=lora_url,
        session_factory=common_session_factory(
            token_settings=TokenSettings(
                client_id=lora_client_id,
                client_secret=lora_client_secret,
                auth_realm=lora_auth_realm,
                auth_server=auth_server,
            )
        ),
    )

    async with AsyncExitStack() as stack:
        mo_graphql_session, mo_client_session, *_ = await asyncio.gather(
            stack.enter_async_context(mo_graphql_client),
            stack.enter_async_context(mo_client),
            stack.enter_async_context(mo_model_client.context()),
            stack.enter_async_context(lora_model_client.context()),
        )
        yield Clients(
            mo_graphql_session=mo_graphql_session,
            mo_client=mo_client_session,
            mo_model_client=mo_model_client,
            lora_model_client=lora_model_client,
        )
