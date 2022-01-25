# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

import logging
import structlog

from os2mo_init.config import settings

_log_level_name = settings.log_level
_log_level_value = logging.getLevelName(_log_level_name)

structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(_log_level_value)
)
