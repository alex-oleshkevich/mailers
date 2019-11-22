import tempfile

import pytest

from mailers.exceptions import ImportFromStringError
from mailers.importer import import_from_string


def test_raises_if_no_semicolon():
    with pytest.raises(ImportFromStringError) as ex:
        import_from_string("some.module")
    assert str(ex.value) == (
        'Import string must be in format: "<module>:<attribute>". '
        f'Given: "some.module"'
    )


def test_raises_if_module_not_found():
    with pytest.raises(ImportFromStringError) as ex:
        import_from_string("some.module:SomeClass")
    assert str(ex.value) == 'Could not import module: "some.module"'


def test_raises_if_attribute_not_found():
    with pytest.raises(ImportFromStringError) as ex:
        import_from_string("tempfile:MissingTemporaryFile")
    assert (
        str(ex.value)
        == 'Attribute "MissingTemporaryFile" not found in module "tempfile".'
    )


def test_imports_attribute():
    klass = import_from_string("tempfile:TemporaryFile")
    assert klass is tempfile.TemporaryFile
