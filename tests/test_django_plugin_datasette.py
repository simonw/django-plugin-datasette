import pytest
from django.core.asgi import get_asgi_application
from djp import asgi_wrapper
from django.test.client import Client
import httpx


@pytest.mark.django_db
def test_index_page_200():
    response = Client().get("/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_asgi_wrapper():
    application = get_asgi_application()
    wrapped_application = asgi_wrapper(application)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=wrapped_application),
        base_url="http://testserver",
    ) as client:
        response = await client.get("http://testserver/-/datasette/")
        assert response.status_code == 200
        assert "<title>Datasette: test</title>" in response.text
