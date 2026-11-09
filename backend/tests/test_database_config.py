import os
import pytest
from app.core.database import normalize_database_url, get_sanitized_db_url
from app.core.config import Settings, INSECURE_DEV_SECRET, LEGACY_INSECURE_SECRET, VERCEL_PRODUCTION_ORIGIN

def test_normalize_database_url_render_postgres():
    render_url = "postgres://myuser:mypassword@dpg-abc1234.oregon-postgres.render.com/mydb_789"
    normalized = normalize_database_url(render_url)
    assert normalized.startswith("postgresql+psycopg2://")
    assert "myuser:mypassword@dpg-abc1234.oregon-postgres.render.com/mydb_789" in normalized

def test_normalize_database_url_standard_postgresql():
    std_url = "postgresql://myuser:mypassword@localhost:5432/mydb"
    normalized = normalize_database_url(std_url)
    assert normalized.startswith("postgresql+psycopg2://")

def test_normalize_database_url_already_explicit_driver():
    explicit_url = "postgresql+psycopg2://myuser:mypassword@localhost:5432/mydb"
    normalized = normalize_database_url(explicit_url)
    assert normalized == explicit_url

def test_normalize_database_url_sqlite_preserved():
    sqlite_url = "sqlite:///./movie_preproduction.db"
    assert normalize_database_url(sqlite_url) == sqlite_url

def test_normalize_database_url_empty_fallback():
    assert normalize_database_url("") == "sqlite:///./movie_preproduction.db"
    assert normalize_database_url("   ") == "sqlite:///./movie_preproduction.db"

def test_get_sanitized_db_url_masks_password():
    url_with_secret = "postgresql+psycopg2://admin:super_secret_password_123@dpg-xyz.render.com:5432/prod_db"
    sanitized = get_sanitized_db_url(url_with_secret)
    assert "super_secret_password_123" not in sanitized
    assert "***" in sanitized
    assert "admin:***@dpg-xyz.render.com:5432" in sanitized

def test_secret_key_fails_in_production_when_empty(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("RENDER", raising=False)
    monkeypatch.setenv("SECRET_KEY", "")

    with pytest.raises(ValueError) as excinfo:
        Settings(ENVIRONMENT="production", SECRET_KEY="")
    assert "CRITICAL CONFIGURATION ERROR: SECRET_KEY" in str(excinfo.value)

def test_secret_key_fails_in_production_with_insecure_default(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("RENDER", raising=False)

    with pytest.raises(ValueError) as excinfo:
        Settings(ENVIRONMENT="production", SECRET_KEY=INSECURE_DEV_SECRET)
    assert "CRITICAL CONFIGURATION ERROR: SECRET_KEY" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        Settings(ENVIRONMENT="production", SECRET_KEY=LEGACY_INSECURE_SECRET)
    assert "CRITICAL CONFIGURATION ERROR: SECRET_KEY" in str(excinfo.value)

def test_secret_key_succeeds_in_production_with_valid_secret(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("RENDER", raising=False)
    valid_secret = "production_super_strong_custom_random_token_9999"
    s = Settings(ENVIRONMENT="production", SECRET_KEY=valid_secret)
    assert s.SECRET_KEY == valid_secret

def test_secret_key_allows_dev_fallback_in_development(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.delenv("RENDER", raising=False)
    monkeypatch.delenv("SECRET_KEY", raising=False)
    s = Settings(ENVIRONMENT="development", SECRET_KEY="")
    assert s.SECRET_KEY == INSECURE_DEV_SECRET

def test_cors_origins_comma_separated_string(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "development")
    s = Settings(
        ENVIRONMENT="development",
        CORS_ORIGINS="https://movie-preproduction70mm.vercel.app, https://staging-preview.vercel.app"
    )
    assert "https://movie-preproduction70mm.vercel.app" in s.CORS_ORIGINS
    assert "https://staging-preview.vercel.app" in s.CORS_ORIGINS
    assert len(s.CORS_ORIGINS) == 2

def test_cors_origins_json_array_string(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "development")
    s = Settings(
        ENVIRONMENT="development",
        CORS_ORIGINS='["https://movie-preproduction70mm.vercel.app", "https://custom-domain.org"]'
    )
    assert "https://movie-preproduction70mm.vercel.app" in s.CORS_ORIGINS
    assert "https://custom-domain.org" in s.CORS_ORIGINS
    assert len(s.CORS_ORIGINS) == 2

def test_cors_origins_production_defaults_exclude_localhost(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("RENDER", raising=False)
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    s = Settings(ENVIRONMENT="production", SECRET_KEY="valid_prod_secret_key_12345")
    assert VERCEL_PRODUCTION_ORIGIN in s.CORS_ORIGINS
    for origin in s.CORS_ORIGINS:
        assert "localhost" not in origin
        assert "127.0.0.1" not in origin
