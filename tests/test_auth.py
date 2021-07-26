import time
from unittest.mock import MagicMock

import httpx
import jwt
import pytest
from httpx_iap import IAPAuth, GoogleServiceAccount
from pytest_httpx import HTTPXMock


@pytest.fixture
def auth_with_mocked_account() -> IAPAuth:
    mock_service_account = MagicMock(spec=GoogleServiceAccount)
    mock_service_account.auth_uri = "https://example.invalid"
    mock_service_account.get_bearer_token.return_value = "example_token"
    mock_service_account.async_get_bearer_token.return_value = "example_token"
    auth = IAPAuth("test_client_id", mock_service_account)
    return auth


class TestIAPAuth:
    def test_init(self, test_service_account):
        """Test default init pathway."""
        auth = IAPAuth("test_client_id", test_service_account)
        assert auth.jwt_soft_expiration == 1800

    def test_init_dict(self, test_service_account, test_service_account_dict):
        """Test handling of service accounts as dicts."""
        auth = IAPAuth("test_client_id", test_service_account_dict)
        assert test_service_account == auth.service_account

    def test_init_invalid_expiry(self, test_service_account):
        """Test handling of invalid user-provided token expiry."""
        with pytest.raises(ValueError):
            IAPAuth("test_client_id", test_service_account, 10000)

    def test_sync_auth_flow(self, auth_with_mocked_account, httpx_mock: HTTPXMock):
        httpx_mock.add_response()
        httpx.get("https://example-iap-route.invalid", auth=auth_with_mocked_account)

        requests = httpx_mock.get_requests()
        assert requests[0].headers["Authorization"] == "Bearer example_token"

    @pytest.mark.asyncio
    async def test_async_auth_flow(self, auth_with_mocked_account, httpx_mock: HTTPXMock):
        httpx_mock.add_response()
        async with httpx.AsyncClient(auth=auth_with_mocked_account) as client:
            await client.get("https://example-iap-route.invalid")

        requests = httpx_mock.get_requests()
        assert requests[0].headers["Authorization"] == "Bearer example_token"

    def test_is_jwt_expired_true(self, auth_with_mocked_account):
        payload = {"aud": "fake.apps.googleusercontent.com", "azp": "example@example.iam.gserviceaccount.com",
                   "email": "example@example.iam.gserviceaccount.com", "email_verified": True,
                   "exp": time.time() - 9000, "iat": time.time() - 10000, "iss": "https://accounts.google.com",
                   "sub": "1234", }

        dummy_jwt = jwt.encode(payload, "secret")

        auth_with_mocked_account.google_iap_jwt = dummy_jwt
        assert auth_with_mocked_account.is_jwt_expired is True

    def test_is_jwt_expired_missing(self, auth_with_mocked_account):
        """Assert function returns true when no JWT is set."""
        assert auth_with_mocked_account.is_jwt_expired is True
        auth_with_mocked_account.google_iap_jwt = None

    def test_is_jwt_expired_false(self, auth_with_mocked_account):
        payload = {"aud": "fake.apps.googleusercontent.com", "azp": "example@example.iam.gserviceaccount.com",
                   "email": "example@example.iam.gserviceaccount.com", "email_verified": True,
                   "exp": time.time() + 3600, "iat": time.time(), "iss": "https://accounts.google.com", "sub": "1234", }
        dummy_jwt = jwt.encode(payload, "secret")

        auth_with_mocked_account.google_iap_jwt = dummy_jwt
        assert auth_with_mocked_account.is_jwt_expired is False
