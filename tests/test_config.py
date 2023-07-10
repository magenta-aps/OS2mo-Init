# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from io import BytesIO
from io import TextIOWrapper
from textwrap import dedent

from os2mo_init.config import get_config


def test_get_config() -> None:
    config_str = dedent(
        """
        root_organisation:
          name: "deprecated"
          user_key: "deprecated"
          municipality_code: 123
        facets:
          org_unit_address_type:
            PhoneUnit:
              title: "Telefon"
              scope: "PHONE"
        it_systems:
          AD: "Active Directory"
    """
    )
    config_bytes = BytesIO(config_str.encode())
    config_text = TextIOWrapper(config_bytes)
    config = get_config(config_text)
    assert config.dict() == {
        "root_organisation": {
            "municipality_code": 123,
        },
        "facets": {
            "org_unit_address_type": {
                "PhoneUnit": {
                    "scope": "PHONE",
                    "title": "Telefon",
                },
            }
        },
        "it_systems": {
            "AD": "Active Directory",
        },
    }
