"""Tests for USER_AGENT configuration and error messages."""
import pytest
from types import SimpleNamespace
from imdbinfo import services


def test_user_agent_is_defined():
    """Test that USER_AGENTS_LIST module variable is defined."""
    assert hasattr(services, "USER_AGENTS_LIST")
    assert isinstance(services.USER_AGENTS_LIST, list)
    assert len(services.USER_AGENTS_LIST) > 0


def test_user_agent_can_be_overridden(monkeypatch):
    """Test that USER_AGENTS_LIST can be overridden by users."""
    # Store original USER_AGENTS_LIST
    original_ua = services.USER_AGENTS_LIST
    
    # Override USER_AGENTS_LIST
    custom_ua = "CustomUserAgent/1.0"
    services.USER_AGENTS_LIST = [custom_ua]
    
    # Mock the niquests.get to capture the headers
    captured_headers = {}
    
    def mock_get(url, headers=None, **kwargs):
        captured_headers.update(headers or {})
        html = b'<html><script id="__NEXT_DATA__">{"props":{"pageProps":{"aboveTheFoldData":{"id":"tt0133093"}}}}</script></html>'
        return SimpleNamespace(status_code=200, content=html)
    
    monkeypatch.setattr(services.niquests, "get", mock_get)
    
    # Call get_movie and check the User-Agent used
    try:
        services.get_movie.cache_clear()  # Clear cache to ensure fresh request
        services.get_movie("tt0133093")
    except Exception:
        pass  # We only care about the headers being captured
    
    # Verify custom User-Agent was used
    assert captured_headers.get("User-Agent") == custom_ua
    
    # Restore original USER_AGENTS_LIST
    services.USER_AGENTS_LIST = original_ua


def test_error_message_includes_status_code(monkeypatch):
    """Test that error messages include HTTP status code."""
    def mock_get_with_error(*args, **kwargs):
        return SimpleNamespace(
            status_code=404,
            text="Not Found",
            content=b"Not Found"
        )
    
    monkeypatch.setattr(services.niquests, "get", mock_get_with_error)
    
    with pytest.raises(Exception) as exc_info:
        services.get_movie.cache_clear()
        services.get_movie("tt9999999")
    
    # Check that the error message includes the status code
    assert "HTTP 404" in str(exc_info.value)
    assert "https://www.imdb.com" in str(exc_info.value)


def test_error_message_includes_response_text(monkeypatch):
    """Test that error messages include response text when available."""
    def mock_get_with_error(*args, **kwargs):
        return SimpleNamespace(
            status_code=500,
            text="Internal Server Error - Something went wrong",
            content=b"Internal Server Error"
        )
    
    monkeypatch.setattr(services.niquests, "get", mock_get_with_error)
    
    with pytest.raises(Exception) as exc_info:
        services.get_movie.cache_clear()
        services.get_movie("tt0133093")
    
    # Check that the error message includes both status code and response text
    error_msg = str(exc_info.value)
    assert "HTTP 500" in error_msg
    assert "Internal Server Error" in error_msg


def test_get_name_error_message_includes_details(monkeypatch):
    """Test that get_name error messages include HTTP details."""
    def mock_get_with_error(*args, **kwargs):
        return SimpleNamespace(
            status_code=403,
            text="Forbidden",
            content=b"Forbidden"
        )
    
    monkeypatch.setattr(services.niquests, "get", mock_get_with_error)
    
    with pytest.raises(Exception) as exc_info:
        services.get_name.cache_clear()
        services.get_name("nm9999999")
    
    # Check that the error message includes the status code
    error_msg = str(exc_info.value)
    assert "HTTP 403" in error_msg
    assert "https://www.imdb.com" in error_msg


def test_get_season_episodes_error_message_includes_details(monkeypatch):
    """Test that get_season_episodes error messages include HTTP details."""
    def mock_get_with_error(*args, **kwargs):
        return SimpleNamespace(
            status_code=400,
            text="Bad Request",
            content=b"Bad Request"
        )
    
    monkeypatch.setattr(services.niquests, "get", mock_get_with_error)
    
    with pytest.raises(Exception) as exc_info:
        services.get_season_episodes.cache_clear()
        services.get_season_episodes("tt0133093", season=1)
    
    # Check that the error message includes the status code
    error_msg = str(exc_info.value)
    assert "HTTP 400" in error_msg
    assert "episodes" in error_msg


def test_graphql_error_message_includes_title_id():
    """Test that GraphQL error messages include the title/person ID."""
    # Since we can't easily mock post in the stubbed niquests module,
    # we test this directly by calling the function with a mocked module
    from types import SimpleNamespace
    
    # Save the original module
    original_niquests = services.niquests
    
    try:
        # Create a mock that has both get and post
        def mock_post_with_http_error(*args, **kwargs):
            return SimpleNamespace(
                status_code=500,
                text="Internal Server Error",
                json=lambda: {}
            )
        
        # Create new namespace with both get and post
        mock_niquests = SimpleNamespace(
            get=original_niquests.get,
            post=mock_post_with_http_error
        )
        
        # Replace the module
        services.niquests = mock_niquests
        
        with pytest.raises(Exception) as exc_info:
            services._get_extended_title_info.cache_clear()
            services._get_extended_title_info("0133093")
        
        # Check that the error message includes the IMDb ID and HTTP status
        error_msg = str(exc_info.value)
        assert "tt0133093" in error_msg
        assert "HTTP 500" in error_msg
    finally:
        # Restore original module
        services.niquests = original_niquests


def test_graphql_error_response_includes_details():
    """Test that GraphQL error responses include error details."""
    from types import SimpleNamespace
    
    # Save the original module
    original_niquests = services.niquests
    
    try:
        # Create a mock that returns GraphQL errors
        def mock_post_with_graphql_error(*args, **kwargs):
            return SimpleNamespace(
                status_code=200,
                text="OK",
                json=lambda: {"errors": [{"message": "Invalid ID"}]}
            )
        
        # Create new namespace with both get and post
        mock_niquests = SimpleNamespace(
            get=original_niquests.get,
            post=mock_post_with_graphql_error
        )
        
        # Replace the module
        services.niquests = mock_niquests
        
        with pytest.raises(Exception) as exc_info:
            services._get_extended_title_info.cache_clear()
            services._get_extended_title_info("0133093")
        
        # Check that the error message includes the IMDb ID and GraphQL error details
        error_msg = str(exc_info.value)
        assert "tt0133093" in error_msg
        assert "GraphQL error" in error_msg
    finally:
        # Restore original module
        services.niquests = original_niquests
