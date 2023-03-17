from datetime import timedelta, datetime

import jwt
from logrich.logger_ import log  # noqa
from src.docx.config import config
from src.docx.schemas import (
    TokenCustomModel,
    SecretType,
    get_secret_value,
)


def generate_jwt(
    data: dict,
    lifetime: timedelta | None = None,
    secret: SecretType = config.PRIVATE_KEY,
    algorithm: str = config.JWT_ALGORITHM,
) -> str:
    """only for tests"""
    if not lifetime:
        lifetime = timedelta(days=config.JWT_ACCESS_KEY_EXPIRES_TIME_DAYS)

    data["exp"] = datetime.utcnow() + lifetime
    # log.trace(data)
    payload = TokenCustomModel(**data)
    # log.debug(payload)
    return jwt.encode(
        payload=payload.dict(exclude_none=True),
        key=get_secret_value(secret),
        algorithm=algorithm,
    )
