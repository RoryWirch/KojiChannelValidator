import pytest
import requests
import yaml
import channel_validator as cv
from tests.util import FakeCall
from tests.util import FakeResponse


@pytest.fixture
def fake_request(monkeypatch):
    """Fake for requests.get()"""

    def fake_get(url):
        return FakeResponse(url)

    monkeypatch.setattr(requests, "get", fake_get)


class MockSession:
    def __getattr__(self, name):
        return FakeCall(name)


def test_collect_channels():
    """
    Tests for functioning of collect_channels function
    """
    channel_list = cv.collect_channels(MockSession())

    assert len(channel_list) == 37


def test_get_hw_info(test_host_with_build, fake_request):
    """
    Tests for functioning of collect_hw_info function
    """
    expected = {
        "arches": ["ppc", "ppc64le"],
        "CPU(s)": 8,
        "Ram": 24050560,
        "Disk": "198G",
        "Kernel": "4.18.0-193.28.1.el8_2.ppc64le",
        "Operating System": "RedHat 8.2",
    }
    my_host = test_host_with_build
    my_host.get_hw_info(MockSession())

    assert my_host.hw_dict == expected


def test_config_checker(test_channel_with_hosts):
    """
    Tests that channel.config_check and compare_hosts is working
    """
    channel = test_channel_with_hosts
    channel.config_check()

    config_items = sum([len(elem) for elem in channel.config_groups])

    assert config_items == 8 and len(channel.config_groups) == 5


@pytest.fixture
def test_channel_with_hosts():
    """
    Sets up a test channel with hosts for config checking
    """
    test_channel = cv.channel(name="dummy-rhel8", id=21)

    # set up hosts for the channel. Host data is loaded from .yml
    with open("tests/fixtures/hosts/hosts.yml", "r") as fp:
        host_yml = yaml.safe_load(fp)

        for hosts in host_yml:
            cur_yml = host_yml[hosts]
            tmp_host = cv.host(
                cur_yml["Name"],
                cur_yml["id"],
                cur_yml["enabled"],
                cur_yml["arches"],
                cur_yml["description"],
            )
            for key in tmp_host.hw_dict:
                tmp_host.hw_dict[key] = cur_yml[key]
            test_channel.host_list.append(tmp_host)

    return test_channel


@pytest.fixture
def test_host_with_build(host_94_list_host):
    """
    Sets up host to mock host 94 for testing.
    """
    test_task = cv.task(
        task_id=40263182,
        parent_id=40263155,
        build_info={
            "build_id": 1757570,
            "completion_time": "2021-10-11 18:33:52.018836",
            "completion_ts": 1633977232.01884,
            "creation_event_id": 41464043,
            "creation_time": "2021-10-11 18:30:42.450638",
            "creation_ts": 1633977042.45064,
            "epoch": None,
            "extra": {
                "source": {
                    "original_url": "git://pkgs.devel.redhat.com/rpms/e2e-module-test?#0fb8c7868015e81b4ef62168cb0a71ce70f7dd2b"
                }
            },
            "name": "e2e-module-test",
            "nvr": "e2e-module-test-1.0.4127-1.module+e2e+12941+acfc830c",
            "owner_id": 4066,
            "owner_name": "mbs",
            "package_id": 71581,
            "package_name": "e2e-module-test",
            "release": "1.module+e2e+12941+acfc830c",
            "source": "git://pkgs.devel.redhat.com/rpms/e2e-module-test#0fb8c7868015e81b4ef62168cb0a71ce70f7dd2b",
            "start_time": "2021-10-11 18:30:42.443708",
            "start_ts": 1633977042.44371,
            "state": 1,
            "task_id": 40263155,
            "version": "1.0.4127",
            "volume_id": 9,
            "volume_name": "rhel-8",
        },
    )
    test_host = cv.host(
        "rhel8", 94, True, host_94_list_host["arches"], host_94_list_host["description"]
    )
    test_host.task_list.append(test_task)
    return test_host


@pytest.fixture
def host_94_list_host():
    """
    contains the listHost dictionary for host 94
    """
    return {
        "arches": "ppc ppc64le",
        "capacity": 3.0,
        "comment": "upgrade-brew playbook",
        "description": "Updated: 2021-06-24\n"
        "Infrastructure Type: NA\n"
        "Operating System: RedHat 8.2\n"
        "Kernel: 4.18.0-193.28.1.el8_2.ppc64le\n"
        "vCPU Count: 8\n"
        "Total Memory: 23.497 gb\n",
        "enabled": True,
        "id": 94,
        "name": "ppc-016.build.eng.bos.redhat.com",
        "ready": True,
        "task_load": 0.4,
        "user_id": 1744,
    }
