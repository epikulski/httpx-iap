from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from httpx_iap import GoogleServiceAccount


@pytest.fixture
def test_service_account_dict() -> dict:

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    service_account = {
        "type": "service_account_secret",
        "project_id": "test-project-id",
        "private_key_id": "test_private_key_id",
        "private_key": private_key_bytes.decode(),
        "client_email": "test-service-account-email@test-project.iam.gserviceaccount.com",
        "client_id": "test_client_id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/test-service-account-email%40test-project-id.iam.gserviceaccount.com",
    }
    return service_account


@pytest.fixture
def test_service_account(test_service_account_dict) -> GoogleServiceAccount:
    service_account = GoogleServiceAccount(**test_service_account_dict)
    return service_account
