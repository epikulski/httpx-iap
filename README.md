# httpx-iap
A custom authentication class for [httpx](https://www.python-httpx.org/) to interact with applications secured by [Google IAP](https://cloud.google.com/iap).

Thank you to [Jan Masarik](https://github.com/janmasarik) for `requests-iap`, which this implementation is based upon.

## Installation
```shell
python -m pip install git+https://github.com/epikulski/httpx-iap.git
```

## Usage
```python
import json

import httpx
from httpx_iap import IAPAuth

with open("your-google-service-account.json") as fd:
    service_account_dict = json.load(fd)
    
client_id = "your-client-id-12345.apps.googleusercontent.com"

response = httpx.get(
    "https://your-iap-protected-service.example.com", 
    auth=IAPAuth(client_id=client_id, service_account=service_account_dict)
    )
```

## Development
`httpx_iap` uses [Poetry](https://python-poetry.org/) to manage the development environment. Shortcuts for most development tasks are avaialable
in the project Makefile

```shell
# Configure the environment
make init

# Run linting
make lint

# Run tests
make test
```