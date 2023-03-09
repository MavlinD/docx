from datetime import timedelta, datetime
from typing import Any, Union

import jwt
from jwt import DecodeError
from logrich.logger_ import log
from pydantic import SecretStr, BaseModel
from src.docx.config import config
from src.docx.exceptions import InvalidVerifyToken
from src.docx.schemas import TokenCustomModel

SecretType = Union[str, SecretStr]


def get_secret_value(secret: SecretType) -> str:
    if isinstance(secret, SecretStr):
        return secret.get_secret_value()
    return secret


def decode_jwt(
    encoded_jwt: str,
    algorithms: list[str],
    secret: SecretType = config.PRIVATE_KEY,
    audience: list[str] | str | None = config.TOKEN_AUDIENCE,
) -> dict[str, Any]:
    if algorithms is None:
        algorithms = [config.JWT_ALGORITHM]
    try:
        token = jwt.decode(
            encoded_jwt,
            get_secret_value(secret),
            audience=audience,
            algorithms=algorithms,
        )
        return token
    except (DecodeError, Exception) as err:
        raise InvalidVerifyToken(msg=err)


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
