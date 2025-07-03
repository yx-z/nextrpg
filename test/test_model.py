from dataclasses import dataclass, field, replace

from nextrpg.model import cached, instance_init, register_instance_init


def test_instance_init():
    @register_instance_init
    class MyModel:
        user_input: str
        public_data: str = "public"
        _data2: int = field(default_factory=lambda: 123)
        _data3: int = field(default=456)
        _internal_data: str = instance_init(
            lambda self: f"internal {self.public_data}"
        )

    mm = MyModel("user_input")
    mm.__post_init__()
    assert mm.public_data == "public"
    assert mm._internal_data == "internal public"
    assert replace(mm, public_data="123")._internal_data == "internal public"
    replaced = replace(mm, user_input="abc", _internal_data="def")
    assert replaced.user_input == "abc"
    assert replaced.public_data == "public"
    assert replaced._internal_data == "def"
    assert replaced._data2 == 123
    assert replaced._data3 == 456


def test_cached() -> None:
    @cached(lambda: 1)
    @dataclass
    class MyCache:
        i: int

    a = MyCache(1)
    assert MyCache(1) is a
    b = MyCache(2)
    assert b is not a
    assert MyCache(2) is b

    @cached(lambda: 1, lambda _: None)
    @dataclass
    class MyModel2:
        s: str

    assert MyModel2("a") is not MyModel2("a")