import importlib
from typing import Any

from .exceptions import ImportFromStringError


def import_from_string(spec: str) -> Any:
    if ":" not in spec:
        raise ImportFromStringError(
            'Import string must be in format: "<module>:<attribute>". '
            f'Given: "{spec}"'
        )

    module_name, _, attribute = spec.rpartition(":")
    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, attribute):
            raise ImportFromStringError(
                f'Attribute "{attribute}" not found in module "{module_name}".'
            )

        return getattr(module, attribute)
    except ImportError:
        raise ImportFromStringError(f'Could not import module: "{module_name}"')
