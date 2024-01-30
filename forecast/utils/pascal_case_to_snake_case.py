import re


def pascal_case_split(identifier: str) -> list[str]:
    matches = re.finditer(
        '.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier
    )
    return [m.group(0) for m in matches]


def pascal_case_to_snake_case(identifier: str) -> str:
    return '_'.join(map(str.lower, pascal_case_split(identifier)))
