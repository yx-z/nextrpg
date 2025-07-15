from nextrpg import EventAsAttr, register_rpg_event


def test_event_as_attr() -> None:
    class A(EventAsAttr):
        pass

    @register_rpg_event
    def e() -> None:
        pass

    a = A()
    assert a.e
    assert not e()
