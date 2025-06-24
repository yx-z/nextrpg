from dataclasses import KW_ONLY, field, replace

from nextrpg.model import Model, internal_field


def test_model():
    class MyModel(Model):
        user_input: str
        public_data: str = "public"
        _: KW_ONLY = field()
        _internal_data: str = internal_field(
            lambda self: f"internal {self.public_data}"
        )

    mm = MyModel("user_input")
    assert mm.public_data == "public"
    assert mm._internal_data == "internal public"
    assert replace(mm, public_data="123")._internal_data == "internal public"
    replaced = replace(mm, user_input="abc", _internal_data="def")
    assert replaced.user_input == "abc"
    assert replaced.public_data == "public"
    assert replaced._internal_data == "def"
