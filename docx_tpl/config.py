from dataclasses import dataclass


@dataclass
class Config:
    TEMPLATES_DIR: str = "templates"
    DOWNLOADS_DIR: str = "downloads"
