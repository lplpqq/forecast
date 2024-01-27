from __future__ import annotations

from pathlib import Path
from typing import Self

import yaml
from pydantic import BaseModel

SUPPORTED_EXTENSION: set[str] = set(['yaml', 'json'])


class BaseConfig(BaseModel):
    @classmethod
    def load(cls, path: Path) -> Self:
        formatted_path = str(path.resolve().absolute())

        if not path.exists():
            raise ValueError(f'Config file at "{formatted_path}" doesn\'t exist.')

        if not path.is_file():
            raise ValueError(
                f'Config file path should point to a file. The path: "{formatted_path}"'
            )

        with open(path) as handle:
            file_suffix = path.suffixes[-1][1:]
            if file_suffix == 'json':
                contents = handle.read()
                config = cls.model_validate_json(contents)
            elif file_suffix == 'yaml':
                raw_object = yaml.safe_load(handle)

                config = cls.model_validate(raw_object)
            else:
                raise ValueError(
                    f'File extension ".{file_suffix}" is not supported. Suppored config file extensions: {", ".join(SUPPORTED_EXTENSION)}'
                )

            return config
