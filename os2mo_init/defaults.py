# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
facets = (
    # From os2mo-data-import-and-export/os2mo_data_import/os2mo_data_import/defaults.py
    # Should probably either import from DIPEX, or a test ensuring equivalence, but it
    # is difficult when DIPEX is not made to be imported as a package.
    "org_unit_address_type",
    "employee_address_type",
    "manager_address_type",
    "address_property",
    "engagement_job_function",
    "org_unit_type",
    "engagement_type",
    "association_type",
    "role_type",
    "leave_type",
    "manager_type",
    "responsibility",
    "manager_level",
    "visibility",
    "time_planning",
    "org_unit_level",
    "primary_type",
    "org_unit_hierarchy",
)

classes = {
    # Common classes derived from the following ones:
    #  - os2mo-data-import-and-export/tools/default_mo_setup.py:ensure_default_classes
    #  - os2mo-data-import-and-export/integrations/opus/opus_import.py:OpusImport
    #  - os2mo-data-import-and-export/SD_Lon/sd_importer.py:_add_classes
    "org_unit_address_type": {
        "PhoneUnit": {
            "title": "PHONE",
            "scope": "PHONE",
        },
        "EmailUnit": {
            "title": "EMAIL",
            "scope": "EMAIL",
        },
    },
    "employee_address_type": {
        "PhoneEmployee": {
            "title": "Telefon",
            "scope": "PHONE",
        },
        "AdressePostEmployee": {
            "title": "Postadresse",
            "scope": "DAR",
        },
        "EmailEmployee": {
            "title": "Email",
            "scope": "EMAIL",
        },
    },
    "leave_type": {
        "Orlov": {
            "title": "Orlov",
            "scope": "TEXT",
        },
    },
    "visibility": {
        "Intern": {
            "title": "Må vises internt",
            "scope": "INTERNAL",
        },
        "Public": {
            "title": "Må vises eksternt",
            "scope": "PUBLIC",
        },
        "Secret": {
            "title": "Hemmelig",
            "scope": "SECRET",
        },
    },
    "primary_type": {
        "primary": {
            "title": "Primær",
            "scope": "3000",
        },
        "non-primary": {
            "title": "Ikke-primær ansættelse",
            "scope": "0",
        },
        "explicitly-primary": {
            "title": "Manuelt primær ansættelse",
            "scope": "5000",
        },
    },
}
