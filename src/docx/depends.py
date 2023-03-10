import os

import jwt
from jwt import InvalidAudienceError, ExpiredSignatureError
from logrich.logger_ import log  # noqa

from src.docx.exceptions import InvalidVerifyToken
from src.docx.helpers.tools import get_key
from src.docx.schemas import DocxCreate
from dotenv import load_dotenv

load_dotenv()


async def check_access(payload: DocxCreate) -> bool:
    """Зависимость, авторизует запрос"""
    try:
        token_issuer = payload.token_issuer.upper().strip()
        audience = os.getenv(f"TOKEN_AUDIENCE_{token_issuer}", "")
        algorithm = os.getenv(f"TOKEN_ALGORITHM_{token_issuer}", "")
        pub_key = await get_key(f"public_keys/{payload.token_issuer}.pub")
        # log.info(config.PUBLIC_KEY)
        # log.info(config.PRIVATE_KEY)
        # log.debug(audience)
        # декодируем нагрузку пользовательского токена
        decoded_payload = jwt.decode(
            jwt=payload.token,
            audience=audience,
            key=pub_key,
            algorithms=[algorithm],
        )
        log.debug("", o=decoded_payload)
    except InvalidAudienceError:
        raise InvalidVerifyToken(msg="Некорректная аудиенция")
    except ExpiredSignatureError:
        raise InvalidVerifyToken(msg="Срок действия истёк")
    return True
