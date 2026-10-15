import pytest

from tests.conftest import ensure_disposable


def test_refuses_to_drop_a_database_that_is_not_a_test_database():
    with pytest.raises(pytest.exit.Exception, match="Refusing to drop database 'calls'"):
        ensure_disposable("calls")


def test_accepts_a_test_database():
    ensure_disposable("calls_test")
