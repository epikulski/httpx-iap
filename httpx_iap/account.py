"""
httpx_iap.account

Helper code for handling and authenticating with GCP service accounts.
"""
import time
import typing
from dataclasses import dataclass

import httpx
import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from jwt.utils import force_bytes


@dataclass
class GoogleServiceAccount:  # pylint: disable=too-many-instance-attributes
    """A Google IAM Secret File"""

    type: str
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    client_id: str
    auth_uri: str
    token_uri: str
    auth_provider_x509_cert_url: str
    client_x509_cert_url: str

    def get_jwt_assertion(self, target_audience: str) -> str:
        """Generate a JWT assertion for for a given OIDC audience."""
        message = {
            "kid": self.private_key_id,
            "iss": self.client_email,
            "sub": self.client_email,
            "aud": self.token_uri,
            "iat": int(time.time()),
            "exp": int(time.time()) + 60 * 60,
            "target_audience": target_audience,
        }

        assertion = jwt.encode(
            message,
            load_pem_private_key(  # type: ignore
                force_bytes(self.private_key),
                password=None,
                backend=default_backend(),
            ),
            algorithm="RS256",
        )
        return assertion

    def get_bearer_token(
        self,
        target_audience: str,
        client: httpx.Client,
        grant_type: str = "urn:ietf:params:oauth:grant-type:jwt-bearer",
    ) -> str:
        """Generate an OIDC bear token for the given audience and grant type."""
        response = client.post(
            self.token_uri,
            timeout=4,
            json=self._get_assertion_payload(grant_type, target_audience),
        )

        id_token = response.json()["id_token"]
        return id_token

    async def async_get_bearer_token(
        self,
        target_audience: str,
        client: httpx.AsyncClient,
        grant_type: str = "urn:ietf:params:oauth:grant-type:jwt-bearer",
    ) -> str:
        """Generate an OIDC bear token for the given audience and grant type."""
        response = await client.post(
            self.token_uri,
            timeout=4,
            json=self._get_assertion_payload(grant_type, target_audience),
        )
        response.raise_for_status()
        id_token = response.json()["id_token"]
        return id_token

    def _get_assertion_payload(
        self, grant_type: str, target_audience: str
    ) -> typing.Dict[str, str]:
        request_payload = {
            "grant_type": grant_type,
            "assertion": self.get_jwt_assertion(target_audience),
        }
        return request_payload
