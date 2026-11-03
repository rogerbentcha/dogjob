import secrets
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader

from dogjob.infra.config import get_settings

header_scheme = APIKeyHeader(name="X-API-Key")
ApiKey = Annotated[str, Depends(header_scheme)]

def verify_api_key(key: ApiKey) -> None:
    api_key = get_settings().api_key.get_secret_value()

    # .encode() permet de compater les octects et non les strings
    if not secrets.compare_digest(api_key.encode(), key.encode()):
        raise HTTPException(status_code=401, detail="Invalid API Key",
            headers={"WWW-Authenticate": "APIKey"})
