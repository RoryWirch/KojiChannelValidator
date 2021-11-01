import json
import os
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


@pytest.fixture
def mock_get_build_dict():
    """
    Returns a dictionary of buildID: build info for the mock_get_build function
    """
    build_dict = {
        "1753791": {
            "build_id": 1753791,
            "cg_id": None,
            "cg_name": None,
            "completion_time": "2021-10-07 07:45:39.428208",
            "completion_ts": 1633592739.42821,
            "creation_event_id": 41409357,
            "creation_time": "2021-10-07 07:44:02.519423",
            "creation_ts": 1633592642.51942,
            "epoch": None,
            "extra": {
                "source": {
                    "original_url": "git://pkgs.devel.redhat.com/rpms/convert2rhel#293d829cb317d77c2a4b72dcbb9f39455e604e76"
                }
            },
            "id": 1753791,
            "name": "convert2rhel",
            "nvr": "convert2rhel-0.24-2.el6",
            "owner_id": 3367,
            "owner_name": "mbocek",
            "package_id": 79515,
            "package_name": "convert2rhel",
            "release": "2.el6",
            "source": "git://pkgs.devel.redhat.com/rpms/convert2rhel#293d829cb317d77c2a4b72dcbb9f39455e604e76",
            "start_time": "2021-10-07 07:44:02.511531",
            "start_ts": 1633592642.51153,
            "state": 1,
            "task_id": 40191207,
            "version": "0.24",
            "volume_id": 7,
            "volume_name": "rhel-6",
        },
        "1757570": {
            "build_id": 1757570,
            "cg_id": None,
            "cg_name": None,
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
            "id": 1757570,
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
    }
    return build_dict


@pytest.fixture
def mock_get_build_logs_dict():
    """
    returns a dict of {buildID : [build logs]} for the mock_get_build_logs function
    """
    log_dict = {
        "1753791": [
            {
                "dir": "noarch",
                "name": "state.log",
                "path": "vol/rhel-6/packages/convert2rhel/0.24/2.el6/data/logs/noarch/state.log",
            },
            {
                "dir": "noarch",
                "name": "build.log",
                "path": "vol/rhel-6/packages/convert2rhel/0.24/2.el6/data/logs/noarch/build.log",
            },
            {
                "dir": "noarch",
                "name": "root.log",
                "path": "vol/rhel-6/packages/convert2rhel/0.24/2.el6/data/logs/noarch/root.log",
            },
            {
                "dir": "noarch",
                "name": "mock_output.log",
                "path": "vol/rhel-6/packages/convert2rhel/0.24/2.el6/data/logs/noarch/mock_output.log",
            },
            {
                "dir": "noarch",
                "name": "noarch_rpmdiff.json",
                "path": "vol/rhel-6/packages/convert2rhel/0.24/2.el6/data/logs/noarch/noarch_rpmdiff.json",
            },
        ],
        "1757570": [
            {
                "dir": "aarch64",
                "name": "hw_info.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/aarch64/hw_info.log",
            },
            {
                "dir": "aarch64",
                "name": "state.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/aarch64/state.log",
            },
            {
                "dir": "aarch64",
                "name": "build.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/aarch64/build.log",
            },
            {
                "dir": "aarch64",
                "name": "root.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/aarch64/root.log",
            },
            {
                "dir": "aarch64",
                "name": "installed_pkgs.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/aarch64/installed_pkgs.log",
            },
            {
                "dir": "aarch64",
                "name": "mock_output.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/aarch64/mock_output.log",
            },
            {
                "dir": "i686",
                "name": "hw_info.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/i686/hw_info.log",
            },
            {
                "dir": "i686",
                "name": "state.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/i686/state.log",
            },
            {
                "dir": "i686",
                "name": "build.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/i686/build.log",
            },
            {
                "dir": "i686",
                "name": "root.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/i686/root.log",
            },
            {
                "dir": "i686",
                "name": "installed_pkgs.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/i686/installed_pkgs.log",
            },
            {
                "dir": "i686",
                "name": "mock_output.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/i686/mock_output.log",
            },
            {
                "dir": "ppc64le",
                "name": "hw_info.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/ppc64le/hw_info.log",
            },
            {
                "dir": "ppc64le",
                "name": "state.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/ppc64le/state.log",
            },
            {
                "dir": "ppc64le",
                "name": "build.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/ppc64le/build.log",
            },
            {
                "dir": "ppc64le",
                "name": "root.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/ppc64le/root.log",
            },
            {
                "dir": "ppc64le",
                "name": "installed_pkgs.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/ppc64le/installed_pkgs.log",
            },
            {
                "dir": "ppc64le",
                "name": "mock_output.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/ppc64le/mock_output.log",
            },
            {
                "dir": "s390x",
                "name": "hw_info.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/s390x/hw_info.log",
            },
            {
                "dir": "s390x",
                "name": "state.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/s390x/state.log",
            },
            {
                "dir": "s390x",
                "name": "build.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/s390x/build.log",
            },
            {
                "dir": "s390x",
                "name": "root.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/s390x/root.log",
            },
            {
                "dir": "s390x",
                "name": "installed_pkgs.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/s390x/installed_pkgs.log",
            },
            {
                "dir": "s390x",
                "name": "mock_output.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/s390x/mock_output.log",
            },
            {
                "dir": "x86_64",
                "name": "hw_info.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/x86_64/hw_info.log",
            },
            {
                "dir": "x86_64",
                "name": "state.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/x86_64/state.log",
            },
            {
                "dir": "x86_64",
                "name": "build.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/x86_64/build.log",
            },
            {
                "dir": "x86_64",
                "name": "root.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/x86_64/root.log",
            },
            {
                "dir": "x86_64",
                "name": "installed_pkgs.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/x86_64/installed_pkgs.log",
            },
            {
                "dir": "x86_64",
                "name": "mock_output.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/x86_64/mock_output.log",
            },
        ],
    }
    return log_dict


@pytest.fixture
def test_list_task_data():
    return [
        {
            "arch": "i386",
            "awaited": False,
            "channel_id": 26,
            "completion_time": "2021-06-15 11:05:53.245114",
            "completion_ts": 1623755153.24511,
            "create_time": "2021-06-15 11:03:15.121289",
            "create_ts": 1623754995.12129,
            "host_id": 280,
            "id": 37493015,
            "label": "i686",
            "method": "buildArch",
            "owner": 4132,
            "owner_name": "crecklin",
            "owner_type": 0,
            "parent": 37492841,
            "priority": 19,
            "request": [
                "tasks/2847/37492847/kernel-3.10.0-1160.32.1.el7.1964556.test.cki.src.rpm",
                67194,
                "i686",
                False,
                {"repo_id": 5081187},
            ],
            "result": [
                {
                    "brootid": 7490808,
                    "logs": [
                        "tasks/3015/37493015/build.log",
                        "tasks/3015/37493015/root.log",
                        "tasks/3015/37493015/state.log",
                        "tasks/3015/37493015/mock_output.log",
                    ],
                    "rpms": [
                        "tasks/3015/37493015/kernel-headers-3.10.0-1160.32.1.el7.1964556.test.cki.i686.rpm"
                    ],
                    "srpms": [],
                }
            ],
            "start_time": "2021-06-15 11:04:02.183543",
            "start_ts": 1623755042.18354,
            "state": 2,
            "waiting": None,
            "weight": 2.5,
        }
    ]
