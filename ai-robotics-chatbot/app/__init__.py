"""Package initialization."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    """Factory function to create FastAPI app."""
    from app.main import app
    return app
