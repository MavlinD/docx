from typing import Callable

import docx
from fastapi import FastAPI, Request, Response
from logrich.logger_ import log  # noqa
from starlette.middleware.cors import CORSMiddleware
from starlette_validation_uploadfile import ValidateUploadFileMiddleware


def init_middleware(app: FastAPI) -> None:
    """middleware"""
    origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # app.add_middleware(
    #     ValidateUploadFileMiddleware,
    #     app_path=[
    #         "/api/v1/template-upload",
    #         # "/upload/second",
    #     ],
    #     max_size=16777216,
    #     file_type=["image/png", "image/jpeg"]
    # )

    @app.middleware("http")
    async def request_middleware(request: Request, call_next: Callable) -> Response:
        try:
            log.trace(f"python-docx v.{docx.__version__}")
            response = await call_next(request)
            # log.info(response)
        finally:
            ...
        return response
