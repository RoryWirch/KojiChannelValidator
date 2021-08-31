import pytest
from connection import get_host


def test_get_host_without_env_var():
    # Ensure that we get a SystemExit when we have no PGHOST env var set
    with pytest.raises(SystemExit) as e:
        get_host()
    assert str(e.value) == 'Please set the PGHOST environment'


def test_get_host_with_env_var(monkeypatch):
    # Ensure that we get the PGHOST value
    monkeypatch.setenv('PGHOST', 'db.example.com')
    host = get_host()
    assert host == 'db.example.com'