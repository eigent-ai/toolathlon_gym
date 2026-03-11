#  conftest.py
#
#  Copyright (c) 2025 Junpei Kawamoto
#
#  This software is released under the MIT License.
#
#  http://opensource.org/licenses/mit-license.php
import pytest


@pytest.fixture(scope="module")
def anyio_backend() -> str:
    return "asyncio"
