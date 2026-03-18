import logging
import sys

logger: logging.Logger = logging.getLogger(__name__)


if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


if sys.version_info >= (3, 13):
    from warnings import deprecated
else:
    from typing_extensions import deprecated

__all__ = [
    "deprecated",
    "override",
]
