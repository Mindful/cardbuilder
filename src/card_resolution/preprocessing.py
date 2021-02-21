from typing import Union, List


def default_preprocessing(value: Union[str, List[str]]) -> str:
    if isinstance(value, list):
        return '\n'.join(value)
    elif isinstance(value, str):
        return value
    else:
        raise RuntimeError('Field value must be list of strings or string')


def comma_separated_preprocessing(value: List[str]) -> str:
    return ', '.join(value)