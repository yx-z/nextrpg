from pytest import raises

from nextrpg.config import Config, DebugConfig
from nextrpg.logger import FROM_CONFIG, Logger
from test.util import override_config


@override_config(Config(debug=DebugConfig()))
def test_logger():
    logger = Logger("TestLogger")
    i = 1
    logger.info("Info {i}")
    logger.warning("Warning {i}", duration=FROM_CONFIG)
    logger.error("Error {i}", duration=123)
    logger.error("Error {i}", duration=123)

    with raises(ValueError):
        Logger("TestLogger")
