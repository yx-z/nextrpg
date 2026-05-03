import pytest
from nextrpg.core.util import type_name, generator_name
from nextrpg.core.module_and_attribute import ModuleAndAttribute, to_module_and_attribute

def test_type_name():
    assert type_name(int) == "int"
    assert type_name(1) == "int"

def test_generator_name():
    def my_gen():
        yield 1
    g = my_gen()
    assert generator_name(g) == "my_gen"
    # Test with non-generator object that might have __name__
    assert generator_name(iter([1, 2])) == "list_iterator"

def test_module_and_attribute_extended():
    ma = ModuleAndAttribute("nextrpg.core.util", "type_name")
    assert ma.qualname == "nextrpg.core.util.type_name"
    assert ma.save_data == ("nextrpg.core.util", "type_name")
    assert ma.imported == type_name
    
    ma2 = ModuleAndAttribute.load_from_save(["nextrpg.core.util", "type_name"])
    assert ma2 == ma
    
    ma3 = to_module_and_attribute(type_name)
    assert ma3.module == "nextrpg.core.util"
    assert ma3.attribute == "type_name"

def test_module_and_attribute_load_error():
    with pytest.raises(AssertionError):
        ModuleAndAttribute.load_from_save(["too", "many", "items"])
