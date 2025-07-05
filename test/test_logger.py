from pytest import raises

from nextrpg.config import Config, DebugConfig
from nextrpg.logger import FROM_CONFIG, Logger
from test.util import override_config


@override_config(Config(debug=DebugConfig()))
def test_logger():
    logger = Logger("TestLogget")
    i = 1
    logger.info(t"Info {i}")
    logger.warning(t"Warning {i}", duration=FROM_CONFIG)
    logger.error(t"Error {i}", duration=123)
    logger.error(t"Error {i}", duration=123)

    with raises(ValueError):
        Logger("TestLogget")
