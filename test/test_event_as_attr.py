from nextrpg import event_as_attr, register_rpg_event


def test_event_as_attr() -> None:
    @event_as_attr
    class A:
        pass

    @register_rpg_event
    def e() -> None:
        pass

    a = A()
    assert a.e
    assert not e()
