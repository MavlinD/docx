from datetime import timedelta, datetime
from typing import Union

import jwt
from jwt import InvalidAudienceError, ExpiredSignatureError, DecodeError
from logrich.logger_ import log  # noqa
from pydantic import SecretStr
from src.docx.config import config
from src.docx.exceptions import InvalidVerifyToken, ErrorCodeLocal
from src.docx.helpers.tools import get_key
from src.docx.schemas import TokenCustomModel, DocxCreate


SecretType = Union[str, SecretStr]


def get_secret_value(secret: SecretType) -> str:
    if isinstance(secret, SecretStr):
        return secret.get_secret_value()
    return secret


async def decode_jwt(
    payload: DocxCreate,
    audience: str,
) -> None:
    try:
        # сначала установим издателя токена, для этого прочитаем нагрузку без валидации.
        claimset_without_validation = jwt.decode(
            jwt=payload.token, options={"verify_signature": False}
        )
        token_issuer = (
            claimset_without_validation.get("iss", "").strip().replace(".", "_").replace("-", "_")
        )
        header = jwt.get_unverified_header(payload.token)
        algorithm = header.get("alg", "")
        if algorithm not in config.ALGORITHMS_WHITE_LIST:
            log.err("алгоритм подписи токена странен(", o=header)
            raise InvalidVerifyToken(msg=ErrorCodeLocal.TOKEN_ALGORITHM_NOT_FOUND.value)
        # определяем наличие разрешения
        pub_key = await get_key(f"public_keys/{token_issuer.lower()}.pub")
        # log.info(config.PUBLIC_KEY)
        # log.info(config.PRIVATE_KEY)
        # log.debug(audience)
        # валидируем токен
        jwt.decode(
            jwt=payload.token,
            audience=audience,
            key=pub_key,
            algorithms=[algorithm],
        )
        # log.debug("", o=decoded_payload)
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
