# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
from .cli import run

if __name__ == "__main__":
    run(
        prog_name=__package__,  # prevents 'Usage: __main__.py [OPTIONS]'
        auto_envvar_prefix="OS2MO_INIT",
    )
