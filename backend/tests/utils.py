from fastapi.testclient import TestClient

from app.core.config import settings

url_login = f"{settings.API_V1_STR}/login/access_token"


def get_admin_header(client: TestClient) -> dict[str, str]:
    """Get header with authorization token for the admin user."""
    login = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    response = client.post(url_login, data=login)
    tokens = response.json()
    a_token = tokens.get("access_token")
    return {"Authorization": f"Bearer {a_token}"}


def get_standard_header(client: TestClient) -> dict[str, str]:
    """Get header with authorization token for the standard user."""
    login = {
        "username": "Tracy",
        "password": "Chapman",
    }
    response = client.post(url_login, data=login)
    tokens = response.json()
    a_token = tokens.get("access_token")
    return {"Authorization": f"Bearer {a_token}"}
