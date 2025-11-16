import os
import pytest
from imdbinfo import config


def test_get_ssl_verify_default():
    """Test that SSL verification is enabled by default"""
    # By default, SSL verification should be enabled
    assert config.get_ssl_verify() is True


def test_set_ssl_verify():
    """Test setting SSL verification"""
    original_value = config.get_ssl_verify()
    
    try:
        # Test disabling SSL verification
        config.set_ssl_verify(False)
        assert config.get_ssl_verify() is False
        
        # Test enabling SSL verification
        config.set_ssl_verify(True)
        assert config.get_ssl_verify() is True
    finally:
        # Restore original value
        config.set_ssl_verify(original_value)


def test_ssl_verify_env_variable(monkeypatch):
    """Test SSL verification controlled by environment variable"""
    # Test with IMDBINFO_VERIFY_SSL=false
    monkeypatch.setenv("IMDBINFO_VERIFY_SSL", "false")
    # Need to reload the module to pick up the env variable
    import importlib
    importlib.reload(config)
    assert config.get_ssl_verify() is False
    
    # Test with IMDBINFO_VERIFY_SSL=true
    monkeypatch.setenv("IMDBINFO_VERIFY_SSL", "true")
    importlib.reload(config)
    assert config.get_ssl_verify() is True
    
    # Test with IMDBINFO_VERIFY_SSL=False (uppercase)
    monkeypatch.setenv("IMDBINFO_VERIFY_SSL", "False")
    importlib.reload(config)
    assert config.get_ssl_verify() is False
    
    # Test with default (no env variable)
    monkeypatch.delenv("IMDBINFO_VERIFY_SSL", raising=False)
    importlib.reload(config)
    assert config.get_ssl_verify() is True
