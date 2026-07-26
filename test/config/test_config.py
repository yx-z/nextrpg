import pytest
from nextrpg.config.config import Config, config, force_debug_config, initial_config, override_config, set_config
from nextrpg.config.debug_config import DebugConfig

def test_config_singleton():
    """Test that config() returns a singleton instance."""
    cfg1 = config()
    cfg2 = config()
    assert cfg1 is cfg2
    assert isinstance(cfg1, Config)

def test_initial_config():
    """Test initial_config() behavior."""
    init_cfg = initial_config()
    assert isinstance(init_cfg, Config)
    # The first config created is the initial config
    assert init_cfg is config()

def test_override_config():
    """Test context manager for overriding config."""
    original = config()
    new_cfg = Config(debug=DebugConfig(player_collide_with_others=False))
    
    with override_config(new_cfg) as overridden:
        assert overridden is new_cfg
        assert config() is new_cfg
        assert config().debug.player_collide_with_others is False
        
    # Should revert back to original
    assert config() is original

def test_force_debug_config():
    """Test forcing debug config."""
    # Ensure there is no latest debug config to start
    from nextrpg.config import config as config_module
    original_latest = config_module._latest_debug_config
    config_module._latest_debug_config = None
    
    original_config = config()
    forced = force_debug_config()
    
    assert isinstance(forced, DebugConfig)
    # After calling force_debug_config, _latest_debug_config is set but config().debug might still be None 
    # depending on when it was accessed, but force_debug_config returns the right thing
    assert config_module._latest_debug_config is forced
    
    # Clean up (revert to original)
    set_config(original_config)
    config_module._latest_debug_config = original_latest


def test_force_debug_config_returns_cached():
    """When _latest_debug_config is already set, force_debug_config returns it directly (line 64)."""
    from nextrpg.config import config as config_module

    original_latest = config_module._latest_debug_config
    try:
        cached = DebugConfig()
        config_module._latest_debug_config = cached
        result = force_debug_config()
        assert result is cached
    finally:
        config_module._latest_debug_config = original_latest


def test_initial_config_creates_when_none():
    """When _initial_config is None, initial_config creates and sets it (lines 83-84)."""
    from nextrpg.config import config as config_module

    original_initial = config_module._initial_config
    original_config = config_module._config
    try:
        config_module._initial_config = None
        config_module._config = None
        result = initial_config()
        assert isinstance(result, Config)
        assert config_module._initial_config is result
    finally:
        config_module._initial_config = original_initial
        config_module._config = original_config
