from datetime import timedelta, datetime
from typing import Union

import jwt
from jwt import InvalidAudienceError, ExpiredSignatureError, DecodeError
from logrich.logger_ import log  # noqa
from pydantic import SecretStr
from src.docx.config import config
from src.docx.exceptions import InvalidVerifyToken, ErrorCodeLocal
from src.docx.helpers.tools import get_key
from src.docx.schemas import TokenCustomModel, DocxCreate, Jwt, DocxUpdate, JWToken

SecretType = Union[str, SecretStr]


def get_secret_value(secret: SecretType) -> str:
    if isinstance(secret, SecretStr):
        return secret.get_secret_value()
    return secret


async def decode_jwt(
    payload: DocxCreate | DocxUpdate | JWToken,
    audience: str,
) -> dict[str, str]:
    try:
        # определяем наличие разрешения
        token = Jwt(token=payload.token)
        # log.info(config.PUBLIC_KEY)
        # log.info(config.PRIVATE_KEY)
        # log.debug(audience)
        # валидируем токен
        decoded_payload = jwt.decode(
            jwt=payload.token,
            audience=audience,
            key=await token.pub_key,
            algorithms=[token.algorithm],
        )
        # log.debug("", o=decoded_payload)
        return decoded_payload
    except InvalidAudienceError:
        raise InvalidVerifyToken(msg=ErrorCodeLocal.TOKEN_AUD_NOT_FOUND.value)
    except ExpiredSignatureError:
        raise InvalidVerifyToken(msg=ErrorCodeLocal.TOKEN_EXPIRE.value)
    except ValueError:
        raise InvalidVerifyToken(msg=ErrorCodeLocal.INVALID_TOKEN.value)
    except DecodeError:
        raise InvalidVerifyToken(msg=ErrorCodeLocal.TOKEN_NOT_ENOUGH_SEGMENT.value)


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
