from logging import DEBUG, getLogger

import pytest


@pytest.fixture
def debug():
    """enable debug log"""
    logger = getLogger("packing_packages")
    original_level = logger.level
    logger.setLevel(DEBUG)

    # run test
    yield logger

    # reset logging level
    logger.setLevel(original_level)
