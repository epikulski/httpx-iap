import httpx
import jwt
import pytest
from pytest_httpx import HTTPXMock


class TestGoogleServiceAccount:
    def test_get_jwt_assertion(self, test_service_account):
        """Test formatting of generated assertions."""
        audience = "test_audience"
        assertion = test_service_account.get_jwt_assertion(audience)
        claims = jwt.decode(assertion, options={"verify_signature": False})

        assert claims["kid"] == test_service_account.private_key_id
        assert claims["sub"] == test_service_account.client_email
        assert claims["iss"] == test_service_account.client_email
        assert claims["aud"] == test_service_account.token_uri
        assert isinstance(claims["iat"], int)
        assert isinstance(claims["exp"], int)
        assert claims["target_audience"] == audience

    def test_get_bearer_token(self, test_service_account, httpx_mock: HTTPXMock):
        """Test Google OAuth API called correclty."""
        httpx_mock.add_response(
            url=test_service_account.token_uri, json={"id_token": "test_id_token"}
        )

        with httpx.Client() as client:
            id_token = test_service_account.get_bearer_token("test_audience", client)

        assert id_token == "test_id_token"

    @pytest.mark.asyncio
    async def test_async_get_bearer_token(
        self, test_service_account, httpx_mock: HTTPXMock
    ):
        """Test Google Oauth API called correctly."""
        httpx_mock.add_response(
            url=test_service_account.token_uri, json={"id_token": "test_id_token"}
        )

        async with httpx.AsyncClient() as client:
            id_token = await test_service_account.async_get_bearer_token(
                "test_audience", client
            )

        assert id_token == "test_id_token"
