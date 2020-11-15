from typing import Union, Dict, Iterable


def one_of_includes(check_value: Union[str, Iterable[str], Dict[str]], values_to_check: Iterable[str]):
    return any(x in check_value for x in values_to_check)


def select_key_by_one_of_values_includes(value: str, values_to_check: Dict[str, Iterable]):
    for key in values_to_check:
        if one_of_includes(value, values_to_check[key]):
            return key
    return None
