# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from os2mo_init.util import generate_uuid


def test_generate_uuid():
    assert generate_uuid("test") == UUID("860401e6-779f-71e6-964d-c1b392e6eb0b")
