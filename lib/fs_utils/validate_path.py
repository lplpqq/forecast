import os
from pathlib import Path
from typing import Literal, TypeAlias

from lib.fs_utils.format_path import format_path

AccessMode: TypeAlias = Literal['readable', 'writable', 'executable']

DEFAULT_CHECKS: set[AccessMode] = set(['readable', 'writable'])
ACCESS_MODE_TO_CODE: dict[AccessMode, int] = {
    'readable': os.R_OK,
    'writable': os.W_OK,
    'executable': os.X_OK,
}


def validate_path(
    path: Path,
    type_: Literal['file', 'folder'],
    access_modes_to_check: set[AccessMode] | None = None,
    autocreate_folder: bool = False,
    autocreate_is_recursive: bool = True,
) -> None:
    if access_modes_to_check is None:
        access_modes_to_check = DEFAULT_CHECKS

    formatted_path = format_path(path)
    if not path.exists():
        if type_ == 'folder' and autocreate_folder:
            path.mkdir(parents=autocreate_is_recursive)
        else:
            raise ValueError(
                f'{type_.capitalize()} at "{formatted_path}" doesn\'t exit'
            )

    match type_:
        case 'folder':
            if not path.is_dir():
                raise ValueError(
                    f'Path: "{formatted_path}" has to point to a directory'
                )
        case 'file':
            if not path.is_file():
                raise ValueError(f'Path: "{formatted_path}" has to point to a file')

    for access_mode in access_modes_to_check:
        if not os.access(path, ACCESS_MODE_TO_CODE[access_mode]):
            formatted_wanted_checks = ', '.join(access_modes_to_check)
            raise ValueError(
                f'Path: "{formatted_path} has to be "{formatted_wanted_checks}" but is not {access_mode}'
            )
