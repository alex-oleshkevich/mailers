from email.headerregistry import Address

from mailers.message import AddressList


def test_constructor():
    addresses = AddressList('Root <root@localhost>')
    assert addresses == 'Root <root@localhost>'

    addresses = AddressList(None)
    assert not addresses

    addresses = AddressList(['root@localhost', 'user@localhost'])
    assert addresses == 'root@localhost, user@localhost'

    addresses = AddressList(Address(addr_spec='root@localhost'))
    assert addresses == 'root@localhost'

    addresses = AddressList([Address(addr_spec='root@localhost'), Address(addr_spec='user@localhost')])
    assert addresses == 'root@localhost, user@localhost'


def test_add():
    addresses = AddressList()
    addresses.add('root@localhost', Address(addr_spec='user@localhost'))
    assert addresses == 'root@localhost, user@localhost'


def test_set():
    addresses = AddressList('root@localhost')
    addresses.set('user@localhost')
    assert addresses == 'user@localhost'


def test_clear():
    addresses = AddressList('root@localhost')
    addresses.clear()
    assert addresses.empty


def test_first():
    addresses = AddressList('root@localhost')
    assert addresses.first.addr_spec == 'root@localhost'

    addresses = AddressList()
    assert addresses.first is None


def test_empty():
    addresses = AddressList()
    assert addresses.empty

    addresses.add('root@localhost')
    assert not addresses.empty


def test_iterable():
    addresses = AddressList('root@localhost')
    assert next(iter(addresses)).addr_spec == 'root@localhost'


def test_length():
    addresses = AddressList('root@localhost')
    assert len(addresses) == 1


def test_boolean():
    addresses = AddressList()
    assert not bool(addresses)

    addresses = AddressList('root@localhost')
    assert bool(addresses)


def test_descriptor():
    class T:
        f = AddressList()

    instance = T()
    instance.f = 'root@localhost'
    assert type(instance.f) == AddressList
    assert len(instance.f) == 1

    instance.f = Address(addr_spec='root@localhost')
    assert instance.f == 'root@localhost'

    instance.f = None
    assert instance.f == ''
