from asgiref.sync import sync_to_async
import pytest
from django.core.asgi import get_asgi_application
from django.contrib.auth.models import User
from djp import asgi_wrapper
from django.test.client import Client
import httpx


@pytest.mark.django_db
def test_index_page_200():
    response = Client().get("/")
    assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_asgi_wrapper():
    application = get_asgi_application()
    wrapped_application = asgi_wrapper(application)

    await sync_to_async(User.objects.create)(username="test", password="test")

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=wrapped_application),
        base_url="http://testserver",
    ) as client:
        response = await client.get("http://testserver/-/datasette/")
        assert response.status_code == 200
        assert "<title>Datasette: test</title>" in response.text

        users = (
            await client.get(
                "http://testserver/-/datasette/test/auth_user.json?_shape=array"
            )
        ).json()
        user = users[0]
        # password column must be null
        assert user["username"] == "test"
        assert user["password"] is None
