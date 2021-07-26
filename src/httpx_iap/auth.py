"""
httpx_iap.auth
"""
import asyncio
import threading
import time
import typing

import httpx
import jwt
from httpx_iap.account import GoogleServiceAccount


class IAPAuth(httpx.Auth):
    """Authentication scheme for Google Identity-Aware-Proxy"""

    google_iap_jwt: typing.Optional[str]

    def __init__(  # nosec
        self,
        client_id: str,
        service_account: typing.Union[GoogleServiceAccount, dict],
        jwt_soft_expiration: int = 1800,
        jwt_bearer_token_grant_type: str = "urn:ietf:params:oauth:grant-type:jwt-bearer",
    ):
        self.client_id = client_id

        if isinstance(service_account, GoogleServiceAccount):
            self.service_account = service_account
        else:
            self.service_account = GoogleServiceAccount(**service_account)

        self.google_iap_jwt = None

        # Set the token refresh interval.
        if jwt_soft_expiration > 3600:
            raise ValueError(
                "Parameter `jwt_soft_expiration` should NOT be larger than 3600 seconds (1 hour)!"
            )
        self.jwt_soft_expiration = jwt_soft_expiration

        # This should generally not need to be changed.
        self.jwt_bearer_token_grant_type = jwt_bearer_token_grant_type

        # Set up concurrency locking mechanisms
        self._sync_lock = threading.RLock()
        self._async_lock = asyncio.Lock()

    def sync_auth_flow(self, request: httpx.Request):
        """Set Authorization header on request, fetching token as needed."""
        if not self.google_iap_jwt or self.is_jwt_expired:
            with self._sync_lock as _, httpx.Client() as client:
                self.google_iap_jwt = self.service_account.get_bearer_token(
                    target_audience=self.client_id,
                    client=client,
                    grant_type=self.jwt_bearer_token_grant_type,
                )

        request.headers["Authorization"] = f"Bearer {self.google_iap_jwt}"
        yield request

    async def async_auth_flow(self, request: httpx.Request):
        """Set Authorization header on request, fetching token as needed."""
        if not self.google_iap_jwt or self.is_jwt_expired:
            async with self._async_lock as _, httpx.AsyncClient() as client:
                self.google_iap_jwt = await self.service_account.async_get_bearer_token(
                    target_audience=self.client_id,
                    client=client,
                    grant_type=self.jwt_bearer_token_grant_type,
                )

        request.headers["Authorization"] = f"Bearer {self.google_iap_jwt}"
        yield request

    @property
    def is_jwt_expired(self):
        """
        Check whether the client's JWT is still valid.

        Returns true if the JWT has reached or exceeded the soft expiration.
        """
        if not self.google_iap_jwt:
            return True

        if (
            jwt.decode(self.google_iap_jwt, options={"verify_signature": False})["iat"]
            + self.jwt_soft_expiration
        ) < time.time():
            return True

        return False
