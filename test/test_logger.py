from pytest import raises

from nextrpg import Config, DebugConfig, Logger
from test.util import override_config


@override_config(Config(debug=DebugConfig()))
def test_logger():
    logger = Logger("TestLogger")
    i = 1
    logger.info(t"Info {i}", duration=None)
    logger.warning(t"Warning {i}")
    logger.error(t"Error {i}", duration=123)
    logger.error(t"Error {i}", duration=123)

    with raises(ValueError):
        Logger("TestLogger")
