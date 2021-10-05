import pytest
import koji
import channel_validator as cv

# Session object for use in monkeypatching
mykoji = koji.get_profile_module("brew")
opts = vars(mykoji.config)
session = mykoji.ClientSession(mykoji.config.server, opts)


@pytest.fixture(autouse=True)
def del_session_requests(monkeypatch):
    """
    Delete rsession attr from session to avoid brew API calls
    """
    monkeypatch.delattr(session, "rsession")


def test_task_constructor(test_list_task_data):
    list_task_response = test_list_task_data
    test_task = cv.task(list_task_response[0]["id"], list_task_response[0]["parent"])

    assert test_task.task_id == 37493015 and test_task.parent_id == 37492841


# Class to mock koji session will override responses from brew API calls
class MockSession:

    # mock listChannels always returns a specific testing list
    @staticmethod
    def list_channels():
        return [
            {"id": 1, "name": "default"},
            {"id": 2, "name": "runroot"},
            {"id": 3, "name": "createrepo"},
            {"id": 4, "name": "maven"},
            {"id": 5, "name": "livecd"},
            {"id": 6, "name": "testing"},
            {"id": 7, "name": "runroot-local"},
            {"id": 8, "name": "appliance"},
            {"id": 9, "name": "overflow"},
            {"id": 10, "name": "vm"},
            {"id": 11, "name": "rhel7"},
            {"id": 12, "name": "bluegene"},
            {"id": 13, "name": "dupsign"},
            {"id": 14, "name": "image"},
            {"id": 15, "name": "aarch64"},
            {"id": 16, "name": "ppc64le"},
            {"id": 17, "name": "fedora"},
            {"id": 18, "name": "testing2"},
            {"id": 19, "name": "epel"},
            {"id": 20, "name": "container"},
            {"id": 21, "name": "rhel8"},
            {"id": 22, "name": "retired"},
            {"id": 23, "name": "dupsign-old"},
            {"id": 24, "name": "testing3"},
            {"id": 25, "name": "rhel8-power9"},
            {"id": 26, "name": "rhel7-power8"},
            {"id": 27, "name": "rhel8-z13"},
            {"id": 28, "name": "rhel8-dupsign"},
            {"id": 29, "name": "suse"},
            {"id": 30, "name": "livemedia"},
            {"id": 31, "name": "rhel8-image"},
            {"id": 32, "name": "rhel8-beefy"},
            {"id": 33, "name": "rhel7-beefy"},
            {"id": 34, "name": "maintenance"},
            {"id": 35, "name": "rhel9"},
            {"id": 36, "name": "rhel9-image"},
            {"id": 37, "name": "rhel9-dupsign"},
        ]


@pytest.fixture
def mock_session_response(monkeypatch):
    """
    Mocked responses for brew session
    """

    def mock_list_channels(*args, **kwargs):
        """
        Covers default response of session.listChannels()
        """
        mockSession = MockSession()
        return mockSession.list_channels()

    monkeypatch.setattr(session, "listChannels", mock_list_channels)


def test_collect_channels(mock_session_response):
    """
    Tests for functioning of collect_channels function
    """
    channel_list = cv.collect_channels(session)

    assert len(channel_list) == 37


@pytest.fixture
def test_list_channel_data():
    return [
        {"id": 1, "name": "default"},
        {"id": 2, "name": "runroot"},
        {"id": 3, "name": "createrepo"},
        {"id": 4, "name": "maven"},
        {"id": 5, "name": "livecd"},
        {"id": 6, "name": "testing"},
        {"id": 7, "name": "runroot-local"},
        {"id": 8, "name": "appliance"},
        {"id": 9, "name": "overflow"},
        {"id": 10, "name": "vm"},
        {"id": 11, "name": "rhel7"},
        {"id": 12, "name": "bluegene"},
        {"id": 13, "name": "dupsign"},
        {"id": 14, "name": "image"},
        {"id": 15, "name": "aarch64"},
        {"id": 16, "name": "ppc64le"},
        {"id": 17, "name": "fedora"},
        {"id": 18, "name": "testing2"},
        {"id": 19, "name": "epel"},
        {"id": 20, "name": "container"},
        {"id": 21, "name": "rhel8"},
        {"id": 22, "name": "retired"},
        {"id": 23, "name": "dupsign-old"},
        {"id": 24, "name": "testing3"},
        {"id": 25, "name": "rhel8-power9"},
        {"id": 26, "name": "rhel7-power8"},
        {"id": 27, "name": "rhel8-z13"},
        {"id": 28, "name": "rhel8-dupsign"},
        {"id": 29, "name": "suse"},
        {"id": 30, "name": "livemedia"},
        {"id": 31, "name": "rhel8-image"},
        {"id": 32, "name": "rhel8-beefy"},
        {"id": 33, "name": "rhel7-beefy"},
        {"id": 34, "name": "maintenance"},
        {"id": 35, "name": "rhel9"},
        {"id": 36, "name": "rhel9-image"},
        {"id": 37, "name": "rhel9-dupsign"},
    ]


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


@pytest.fixture
def test_list_hosts_data():
    return [
        {
            "arches": "aarch64",
            "capacity": 6.0,
            "comment": "needs to be restored on ARM HV is there is available capacity",
            "description": "Updated: 2021-05-20\n"
            "Infrastructure Type: ProLiant m400 Server\n"
            "Operating System: RedHat 7.6\n"
            "Kernel: 4.14.0-115.el7a.aarch64\n"
            "vCPU Count: 8\n"
            "Total Memory: 64.851 gb\n",
            "enabled": False,
            "id": 169,
            "name": "arm64-020.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 3407,
        },
        {
            "arches": "aarch64",
            "capacity": 6.0,
            "comment": "needs to be restored on ARM HV is there is available capacity",
            "description": "Updated: 2020-11-30\n"
            "Infrastructure Type: ProLiant m400 Server\n"
            "Operating System: RedHat 7.4\n"
            "Kernel: 4.5.0-15.4.2.el7.aarch64\n"
            "vCPU Count: 8\n"
            "Total Memory: 63.313 gb\n",
            "enabled": False,
            "id": 170,
            "name": "arm64-021.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 3408,
        },
        {
            "arches": "aarch64",
            "capacity": 6.0,
            "comment": "needs to be restored on ARM HV is there is available capacity",
            "description": "Updated: 2020-11-30\n"
            "Infrastructure Type: ProLiant m400 Server\n"
            "Operating System: RedHat 7.6\n"
            "Kernel: 4.14.0-115.32.1.el7a.aarch64\n"
            "vCPU Count: 8\n"
            "Total Memory: 64.851 gb\n",
            "enabled": False,
            "id": 171,
            "name": "arm64-022.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 3409,
        },
        {
            "arches": "s390x",
            "capacity": 2.0,
            "comment": "temp disable "
            "https://projects.engineering.redhat.com/browse/BST-963 "
            "-scmiller\n"
            "\n"
            "2020-11-23, disabled RHELBLD-3837 [tkopecek]",
            "description": "Updated: 2021-03-17\n"
            "Infrastructure Type: NA\n"
            "Operating System: RedHat 7.8\n"
            "Kernel: 4.18.0-80.el8.s390x\n"
            "CPU Count: 8\n"
            "Total Memory: 32.077 gb\n",
            "enabled": False,
            "id": 284,
            "name": "s390-048.build.eng.bos.redhat.com",
            "ready": False,
            "task_load": 0.0,
            "user_id": 4781,
        },
        {
            "arches": "aarch64",
            "capacity": 6.0,
            "comment": "needs to be restored on ARM HV is there is available capacity",
            "description": "Updated: 2020-11-30\n"
            "Infrastructure Type: ProLiant m400 Server\n"
            "Operating System: RedHat 7.4\n"
            "Kernel: 4.5.0-15.4.2.el7.aarch64\n"
            "vCPU Count: 8\n"
            "Total Memory: 63.313 gb\n",
            "enabled": False,
            "id": 168,
            "name": "arm64-019.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 3406,
        },
        {
            "arches": "x86_64 i386",
            "capacity": 4.0,
            "comment": "temporarily running a test",
            "description": "Updated: 2020-11-23\n"
            "Infrastructure Type: KVM\n"
            "Operating System: RedHat 6.10\n"
            "Kernel: 2.6.32-754.15.3.el6.x86_64\n"
            "vCPU Count: 8\n"
            "Total Memory: 8.0 gb\n",
            "enabled": True,
            "id": 280,
            "name": "x86-vm-31.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 4719,
        },
        {
            "arches": "ppc ppc64",
            "capacity": 2.0,
            "comment": "added for Big Endian in RHELBLD-6456",
            "description": "Updated: 2021-07-12\n"
            "Infrastructure Type: NA\n"
            "Operating System: RedHat 6.10\n"
            "Kernel: 2.6.32-754.el6.ppc64\n"
            "vCPU Count: 8\n"
            "Total Memory: 31.597 gb\n",
            "enabled": True,
            "id": 379,
            "name": "ppc64-04.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 6042,
        },
        {
            "arches": "ppc ppc64",
            "capacity": 2.0,
            "comment": "added for Big Endian in RHELBLD-6456",
            "description": "Updated: 2021-07-12\n"
            "Infrastructure Type: NA\n"
            "Operating System: RedHat 6.10\n"
            "Kernel: 2.6.32-754.el6.ppc64\n"
            "vCPU Count: 8\n"
            "Total Memory: 31.597 gb\n",
            "enabled": True,
            "id": 380,
            "name": "ppc64-05.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 6043,
        },
        {
            "arches": "s390x s390",
            "capacity": 3.0,
            "comment": "upgrade-brew playbook",
            "description": "Updated: 2020-11-23\n"
            "Infrastructure Type: NA\n"
            "Operating System: RedHat 6.10\n"
            "Kernel: 2.6.32-754.el6.s390x\n"
            "CPU Count: 4\n"
            "Total Memory: 7.926 gb\n",
            "enabled": True,
            "id": 259,
            "name": "s390-034.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 4541,
        },
        {
            "arches": "s390x s390",
            "capacity": 3.0,
            "comment": "upgrade-brew playbook",
            "description": "Updated: 2020-11-23\n"
            "Infrastructure Type: NA\n"
            "Operating System: RedHat 6.10\n"
            "Kernel: 2.6.32-754.el6.s390x\n"
            "CPU Count: 4\n"
            "Total Memory: 7.926 gb\n",
            "enabled": True,
            "id": 260,
            "name": "s390-036.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 4543,
        },
        {
            "arches": "s390x s390",
            "capacity": 3.0,
            "comment": "upgrade-brew playbook",
            "description": "Updated: 2020-11-23\n"
            "Infrastructure Type: NA\n"
            "Operating System: RedHat 6.10\n"
            "Kernel: 2.6.32-754.el6.s390x\n"
            "CPU Count: 4\n"
            "Total Memory: 7.926 gb\n",
            "enabled": True,
            "id": 261,
            "name": "s390-037.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 4544,
        },
        {
            "arches": "s390x s390",
            "capacity": 3.0,
            "comment": "upgrade-brew playbook",
            "description": "Updated: 2020-11-23\n"
            "Infrastructure Type: NA\n"
            "Operating System: RedHat 6.10\n"
            "Kernel: 2.6.32-754.el6.s390x\n"
            "CPU Count: 4\n"
            "Total Memory: 7.926 gb\n",
            "enabled": True,
            "id": 262,
            "name": "s390-038.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 4545,
        },
        {
            "arches": "s390x s390",
            "capacity": 3.0,
            "comment": "upgrade-brew playbook",
            "description": "Updated: 2020-11-23\n"
            "Infrastructure Type: NA\n"
            "Operating System: RedHat 6.10\n"
            "Kernel: 2.6.32-754.el6.s390x\n"
            "CPU Count: 4\n"
            "Total Memory: 7.926 gb\n",
            "enabled": True,
            "id": 263,
            "name": "s390-039.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 4546,
        },
        {
            "arches": "s390x s390",
            "capacity": 3.0,
            "comment": "upgrade-brew playbook",
            "description": "Updated: 2020-11-23\n"
            "Infrastructure Type: NA\n"
            "Operating System: RedHat 6.10\n"
            "Kernel: 2.6.32-754.el6.s390x\n"
            "CPU Count: 4\n"
            "Total Memory: 7.926 gb\n",
            "enabled": True,
            "id": 266,
            "name": "s390-042.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 4549,
        },
        {
            "arches": "s390x s390",
            "capacity": 3.0,
            "comment": "upgrade-brew playbook",
            "description": "Updated: 2020-11-23\n"
            "Infrastructure Type: NA\n"
            "Operating System: RedHat 6.10\n"
            "Kernel: 2.6.32-754.el6.s390x\n"
            "CPU Count: 4\n"
            "Total Memory: 7.926 gb\n",
            "enabled": True,
            "id": 267,
            "name": "s390-035.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 4550,
        },
        {
            "arches": "x86_64 i386",
            "capacity": 4.0,
            "comment": "",
            "description": "Updated: 2020-11-23\n"
            "Infrastructure Type: KVM\n"
            "Operating System: RedHat 6.10\n"
            "Kernel: 2.6.32-754.15.3.el6.x86_64\n"
            "vCPU Count: 8\n"
            "Total Memory: 8.0 gb\n",
            "enabled": True,
            "id": 279,
            "name": "x86-vm-29.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 4718,
        },
        {
            "arches": "s390x s390",
            "capacity": 4.0,
            "comment": "upgrade-brew playbook",
            "description": "Updated: 2020-11-23\n"
            "Infrastructure Type: NA\n"
            "Operating System: RedHat 6.10\n"
            "Kernel: 2.6.32-754.el6.s390x\n"
            "CPU Count: 8\n"
            "Total Memory: 32.128 gb\n",
            "enabled": True,
            "id": 264,
            "name": "s390-040.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 4547,
        },
        {
            "arches": "s390x s390",
            "capacity": 3.0,
            "comment": "upgrade-brew playbook",
            "description": "Updated: 2020-11-23\n"
            "Infrastructure Type: NA\n"
            "Operating System: RedHat 6.10\n"
            "Kernel: 2.6.32-754.el6.s390x\n"
            "CPU Count: 8\n"
            "Total Memory: 32.128 gb\n",
            "enabled": True,
            "id": 265,
            "name": "s390-041.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 4548,
        },
        {
            "arches": "x86_64 i386",
            "capacity": 4.0,
            "comment": "",
            "description": "Updated: 2020-11-23\n"
            "Infrastructure Type: KVM\n"
            "Operating System: RedHat 6.10\n"
            "Kernel: 2.6.32-754.15.3.el6.x86_64\n"
            "vCPU Count: 24\n"
            "Total Memory: 64.558 gb\n",
            "enabled": True,
            "id": 278,
            "name": "x86-vm-30.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 4717,
        },
        {
            "arches": "x86_64 i386",
            "capacity": 4.0,
            "comment": "",
            "description": "Updated: 2020-11-23\n"
            "Infrastructure Type: KVM\n"
            "Operating System: RedHat 6.10\n"
            "Kernel: 2.6.32-754.15.3.el6.x86_64\n"
            "vCPU Count: 24\n"
            "Total Memory: 64.558 gb\n",
            "enabled": True,
            "id": 281,
            "name": "x86-vm-32.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 4720,
        },
        {
            "arches": "ppc ppc64",
            "capacity": 2.0,
            "comment": "added for Big Endian in RHELBLD-6456",
            "description": "Updated: 2021-07-12\n"
            "Infrastructure Type: NA\n"
            "Operating System: RedHat 6.10\n"
            "Kernel: 2.6.32-754.35.1.el6.ppc64\n"
            "vCPU Count: 8\n"
            "Total Memory: 31.597 gb\n",
            "enabled": True,
            "id": 375,
            "name": "ppc64-01.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 6038,
        },
        {
            "arches": "s390 s390x",
            "capacity": 8.0,
            "comment": "upgrade-brew playbook",
            "description": "Updated: 2021-06-24\n"
            "Infrastructure Type: NA\n"
            "Operating System: RedHat 6.10\n"
            "Kernel: 2.6.32-754.35.1.el6.s390x\n"
            "CPU Count: 4\n"
            "Total Memory: 5.906 gb\n",
            "enabled": True,
            "id": 218,
            "name": "s390-005.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 3930,
        },
        {
            "arches": "i386 x86_64",
            "capacity": 12.0,
            "comment": "upgrade-brew playbook",
            "description": "Updated: 2021-06-24\n"
            "Infrastructure Type: PowerEdge R620\n"
            "Operating System: RedHat 6.10\n"
            "Kernel: 2.6.32-754.35.1.el6.x86_64\n"
            "vCPU Count: 40\n"
            "Total Memory: 64.377 gb\n",
            "enabled": True,
            "id": 147,
            "name": "x86-031.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 1.0,
            "user_id": 2864,
        },
        {
            "arches": "i386 x86_64",
            "capacity": 12.0,
            "comment": "upgrade-brew playbook",
            "description": "Updated: 2021-06-24\n"
            "Infrastructure Type: PowerEdge R620\n"
            "Operating System: RedHat 6.10\n"
            "Kernel: 2.6.32-754.35.1.el6.x86_64\n"
            "vCPU Count: 40\n"
            "Total Memory: 64.377 gb\n",
            "enabled": True,
            "id": 148,
            "name": "x86-032.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.1,
            "user_id": 2865,
        },
        {
            "arches": "i386 x86_64",
            "capacity": 12.0,
            "comment": "RHELBLD-2051",
            "description": "Updated: 2021-06-24\n"
            "Infrastructure Type: PowerEdge R620\n"
            "Operating System: RedHat 6.10\n"
            "Kernel: 2.6.32-754.35.1.el6.x86_64\n"
            "vCPU Count: 40\n"
            "Total Memory: 64.377 gb\n",
            "enabled": True,
            "id": 150,
            "name": "x86-034.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 2867,
        },
        {
            "arches": "i386 x86_64",
            "capacity": 12.0,
            "comment": "temporary testing",
            "description": "Updated: 2021-06-24\n"
            "Infrastructure Type: PowerEdge R620\n"
            "Operating System: RedHat 6.10\n"
            "Kernel: 2.6.32-754.35.1.el6.x86_64\n"
            "vCPU Count: 40\n"
            "Total Memory: 64.377 gb\n",
            "enabled": True,
            "id": 149,
            "name": "x86-033.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 2866,
        },
        {
            "arches": "i386 x86_64",
            "capacity": 12.0,
            "comment": "upgrade-brew playbook",
            "description": "Updated: 2021-06-24\n"
            "Infrastructure Type: PowerEdge R630\n"
            "Operating System: RedHat 6.10\n"
            "Kernel: 2.6.32-754.35.1.el6.x86_64\n"
            "vCPU Count: 24\n"
            "Total Memory: 31.995 gb\n",
            "enabled": True,
            "id": 179,
            "name": "x86-042.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 3489,
        },
        {
            "arches": "x86_64 i386",
            "capacity": 4.0,
            "comment": "",
            "description": "Updated: 2021-06-24\n"
            "Infrastructure Type: KVM\n"
            "Operating System: RedHat 6.10\n"
            "Kernel: 2.6.32-754.35.1.el6.x86_64\n"
            "vCPU Count: 4\n"
            "Total Memory: 22.365 gb\n",
            "enabled": True,
            "id": 273,
            "name": "x86-vm-21.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 4712,
        },
        {
            "arches": "x86_64 i386",
            "capacity": 4.0,
            "comment": "",
            "description": "Updated: 2021-06-24\n"
            "Infrastructure Type: KVM\n"
            "Operating System: RedHat 6.10\n"
            "Kernel: 2.6.32-754.15.3.el6.x86_64\n"
            "vCPU Count: 8\n"
            "Total Memory: 8.0 gb\n",
            "enabled": True,
            "id": 271,
            "name": "x86-vm-24.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 4710,
        },
        {
            "arches": "x86_64 i386",
            "capacity": 4.0,
            "comment": "",
            "description": "Updated: 2021-06-24\n"
            "Infrastructure Type: KVM\n"
            "Operating System: RedHat 6.10\n"
            "Kernel: 2.6.32-754.35.1.el6.x86_64\n"
            "vCPU Count: 4\n"
            "Total Memory: 22.365 gb\n",
            "enabled": True,
            "id": 274,
            "name": "x86-vm-22.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 4713,
        },
        {
            "arches": "x86_64 i386",
            "capacity": 4.0,
            "comment": "",
            "description": "Updated: 2021-06-24\n"
            "Infrastructure Type: KVM\n"
            "Operating System: RedHat 6.10\n"
            "Kernel: 2.6.32-754.el6.x86_64\n"
            "vCPU Count: 4\n"
            "Total Memory: 15.951 gb\n",
            "enabled": True,
            "id": 272,
            "name": "x86-vm-23.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 4711,
        },
        {
            "arches": "x86_64 i386",
            "capacity": 4.0,
            "comment": "",
            "description": "Updated: 2021-06-24\n"
            "Infrastructure Type: KVM\n"
            "Operating System: RedHat 6.10\n"
            "Kernel: 2.6.32-754.el6.x86_64\n"
            "vCPU Count: 4\n"
            "Total Memory: 15.951 gb\n",
            "enabled": True,
            "id": 270,
            "name": "x86-vm-25.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 4709,
        },
        {
            "arches": "x86_64 i386",
            "capacity": 4.0,
            "comment": "",
            "description": "Updated: 2021-06-24\n"
            "Infrastructure Type: KVM\n"
            "Operating System: RedHat 6.10\n"
            "Kernel: 2.6.32-754.15.3.el6.x86_64\n"
            "vCPU Count: 8\n"
            "Total Memory: 8.0 gb\n",
            "enabled": True,
            "id": 276,
            "name": "x86-vm-26.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 4715,
        },
        {
            "arches": "x86_64 i386",
            "capacity": 4.0,
            "comment": "",
            "description": "Updated: 2021-06-24\n"
            "Infrastructure Type: KVM\n"
            "Operating System: RedHat 6.10\n"
            "Kernel: 2.6.32-754.35.1.el6.x86_64\n"
            "vCPU Count: 8\n"
            "Total Memory: 8.0 gb\n",
            "enabled": True,
            "id": 275,
            "name": "x86-vm-27.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 4714,
        },
        {
            "arches": "x86_64 i386",
            "capacity": 4.0,
            "comment": "",
            "description": "Updated: 2021-06-24\n"
            "Infrastructure Type: KVM\n"
            "Operating System: RedHat 6.10\n"
            "Kernel: 2.6.32-754.18.2.el6.x86_64\n"
            "vCPU Count: 8\n"
            "Total Memory: 8.0 gb\n",
            "enabled": True,
            "id": 277,
            "name": "x86-vm-28.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 4716,
        },
        {
            "arches": "ppc ppc64",
            "capacity": 2.0,
            "comment": "added for Big Endian in RHELBLD-6456",
            "description": "Updated: 2021-07-12\n"
            "Infrastructure Type: NA\n"
            "Operating System: RedHat 6.10\n"
            "Kernel: 2.6.32-754.el6.ppc64\n"
            "vCPU Count: 8\n"
            "Total Memory: 31.597 gb\n",
            "enabled": True,
            "id": 377,
            "name": "ppc64-02.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 6040,
        },
        {
            "arches": "ppc ppc64",
            "capacity": 2.0,
            "comment": "added for Big Endian in RHELBLD-6456",
            "description": "Updated: 2021-07-12\n"
            "Infrastructure Type: NA\n"
            "Operating System: RedHat 6.10\n"
            "Kernel: 2.6.32-754.el6.ppc64\n"
            "vCPU Count: 8\n"
            "Total Memory: 31.597 gb\n",
            "enabled": True,
            "id": 378,
            "name": "ppc64-03.build.eng.bos.redhat.com",
            "ready": True,
            "task_load": 0.0,
            "user_id": 6041,
        },
    ]
