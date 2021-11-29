# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from _pytest.monkeypatch import MonkeyPatch
from httpx import AsyncClient
from respx import MockRouter

from os2mo_init import initialisers
from os2mo_init.config import ConfigClass
from os2mo_init.config import ConfigFacet
from os2mo_init.util import generate_uuid


@pytest.mark.asyncio
async def test_ensure_root_organisation_no_existing(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr("os2mo_init.mo.get_root_org", AsyncMock(return_value=None))
    lora_model_client_mock = AsyncMock()

    await initialisers.ensure_root_organisation(
        mo_graphql_session=AsyncMock(),
        lora_model_client=lora_model_client_mock,
        name="my name",
        user_key="my user key",
    )

    lora_model_client_mock.load_lora_objs.assert_awaited_once()
    actual_org = lora_model_client_mock.load_lora_objs.await_args.args[0][0]
    assert (
        actual_org.uuid
        == generate_uuid("organisations.__root__")
        == UUID("67e9a80e-6bc0-e97a-9751-02600c017844")
    )


@pytest.mark.asyncio
async def test_ensure_root_organisation_exising(
    monkeypatch: MonkeyPatch, root_org_uuid: UUID
) -> None:
    monkeypatch.setattr(
        "os2mo_init.mo.get_root_org", AsyncMock(return_value=root_org_uuid)
    )
    lora_model_client_mock = AsyncMock()

    await initialisers.ensure_root_organisation(
        mo_graphql_session=AsyncMock(),
        lora_model_client=lora_model_client_mock,
        name="my name",
        user_key="my user key",
    )

    lora_model_client_mock.load_lora_objs.assert_awaited_once()
    actual_org = lora_model_client_mock.load_lora_objs.await_args.args[0][0]
    assert actual_org.uuid == root_org_uuid


@pytest.mark.asyncio
async def test_ensure_facets(
    async_client: AsyncClient, root_org_uuid: UUID, facets_mock: dict[str, UUID]
) -> None:
    lora_model_client_mock = AsyncMock()

    user_keys = ["leave_type", "my_new_facet"]

    await initialisers.ensure_facets(
        mo_client=async_client,
        lora_model_client=lora_model_client_mock,
        organisation_uuid=root_org_uuid,
        user_keys=user_keys,
    )

    lora_model_client_mock.load_lora_objs.assert_awaited_once()
    actual_facets = lora_model_client_mock.load_lora_objs.await_args.args[0]
    # leave_type updated with original UUID
    assert actual_facets[0].uuid == facets_mock["leave_type"]
    # my_new_facet created with UUID from generate_uuid("facets.my_new_facet")
    assert (
        actual_facets[1].uuid
        == generate_uuid("facets.my_new_facet")
        == UUID("9af06ada-46a2-39a6-ad7c-92c766592e19")
    )


@pytest.mark.asyncio
async def test_ensure_classes(
    async_client: AsyncClient,
    root_org_uuid: UUID,
    facets: dict[str, UUID],
    classes_mock: dict[str, dict[str, dict[str, str]]],
):
    mo_model_client_mock = AsyncMock()
    facet_classes_config = {
        "leave_type": ConfigFacet.parse_obj(
            {
                "Orlov": ConfigClass(
                    title="New Orlov Name",
                    scope="TEXT",
                ),
                "barsel": ConfigClass(
                    title="Barsel",
                    scope="TEXT",
                ),
            }
        )
    }

    await initialisers.ensure_classes(
        mo_client=async_client,
        mo_model_client=mo_model_client_mock,
        organisation_uuid=root_org_uuid,
        facet_classes_config=facet_classes_config,
        facet_uuids=facets,
    )

    mo_model_client_mock.load_mo_objs.assert_awaited_once()
    actual_classes = mo_model_client_mock.load_mo_objs.await_args.args[0]
    # Orlov updated with original UUID
    assert actual_classes[0].uuid == UUID(classes_mock["leave_type"]["Orlov"]["uuid"])
    assert actual_classes[0].name == "New Orlov Name"
    # barsel created with UUID from generate_uuid()
    assert (
        actual_classes[1].uuid
        == generate_uuid("facets.leave_type.classes.barsel")
        == UUID("8a9bfb06-af50-b867-6669-ff098bb74ce6")
    )


@pytest.mark.asyncio
async def test_ensure_it_systems(
    async_client: AsyncClient,
    root_org_uuid: UUID,
    it_systems_mock: dict[str, dict[str, str]],
    respx_mock: MockRouter,
) -> None:
    it_systems_config = {
        "AD": "New AD Name",
        "OpenDesk": "The Open Desk",
    }

    ad_uuid = it_systems_mock["AD"]["uuid"]
    respx_mock.put(
        f"{async_client.base_url}/organisation/itsystem/{ad_uuid}",
        json__attributter__itsystemegenskaber__0__brugervendtnoegle="AD",
        json__attributter__itsystemegenskaber__0__itsystemnavn="New AD Name",
    )
    open_desk_uuid = generate_uuid("it_systems.OpenDesk")
    respx_mock.put(
        f"{async_client.base_url}/organisation/itsystem/{open_desk_uuid}",
        json__attributter__itsystemegenskaber__0__brugervendtnoegle="OpenDesk",
        json__attributter__itsystemegenskaber__0__itsystemnavn="The Open Desk",
    )

    await initialisers.ensure_it_systems(
        mo_client=async_client,
        lora_client=async_client,
        organisation_uuid=root_org_uuid,
        it_systems_config=it_systems_config,
    )

    assert open_desk_uuid == UUID("d2ef5d9a-d5dc-a522-1df1-62cecf012c92")
    respx_mock.assert_all_called()
