import json
import os
import pytest
import koji
import requests
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


TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(TESTS_DIR, "fixtures")


class FakeCall:
    def __init__(self, name):
        self.name = name

    def __call__(self, *args, **kwargs):
        if self.name == "getBuildLogs":
            filename = str(args[0]) + ".json"
            fixture = os.path.join(FIXTURES_DIR, "calls", "getBuildLogs", filename)
        else:
            filename = self.name + ".json"
            fixture = os.path.join(FIXTURES_DIR, "calls", filename)
        try:
            with open(fixture) as fp:
                return json.load(fp)
        except FileNotFoundError:
            print("Create new fixture file at %s" % fixture)
            print("koji call %s ... --json-output > %s" % (self.name, fixture))
            raise


# Class to mock koji session will override responses from brew API calls
class MockSession:
    def __getattr__(self, name):
        return FakeCall(name)

    # mock get_build returns test data to mock session.getBuild()
    @staticmethod
    def get_build(build_id):
        """
        returns the test build info for a given build id
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
        return build_dict[build_id]
        

    @staticmethod
    def requests_get(url):
        """
        returns test log string for requests.get(url) for log collection
        """
        response_dict = {
            "http://download.devel.redhat.com/brewroot/vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/aarch64/hw_info.log": "CPU info:\nArchitecture:        aarch64\nByte Order:          Little Endian\nCPU(s):              16\nOn-line CPU(s) list: 0-15\nThread(s) per core:  1\nCore(s) per cluster: 16\nSocket(s):           -\nCluster(s):          1\nNUMA node(s):        1\nVendor ID:           Cavium\nModel:               1\nModel name:          ThunderX2 99xx\nStepping:            0x1\nBogoMIPS:            400.00\nNUMA node0 CPU(s):   0-15\nFlags:               fp asimd evtstrm aes pmull sha1 sha2 crc32 atomics cpuid asimdrdm\n\n\nMemory:\n              total        used        free      shared  buff/cache   available\nMem:       16175168     1101376    12931904       71296     2141888    12707584\nSwap:       8392640      242304     8150336\n\n\nStorage:\nFilesystem             Size  Used Avail Use% Mounted on\n/dev/mapper/rhel-root  205G  5.9G  199G   3% /\n",
            "http://download.devel.redhat.com/brewroot/vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/ppc64le/hw_info.log": "CPU info:\nArchitecture:        ppc64le\nByte Order:          Little Endian\nCPU(s):              8\nOn-line CPU(s) list: 0-7\nThread(s) per core:  1\nCore(s) per socket:  8\nSocket(s):           1\nNUMA node(s):        1\nModel:               2.1 (pvr 004b 0201)\nModel name:          POWER8 (architected), altivec supported\nHypervisor vendor:   KVM\nVirtualization type: para\nL1d cache:           64K\nL1i cache:           32K\nNUMA node0 CPU(s):   0-7\n\n\nMemory:\n              total        used        free      shared  buff/cache   available\nMem:       24050560     1062144    16829376      158912     6159040    22675264\nSwap:      15744960       64000    15680960\n\n\nStorage:\nFilesystem             Size  Used Avail Use% Mounted on\n/dev/mapper/rhel-root  198G  6.3G  192G   4% /\n",
            "http://download.devel.redhat.com/brewroot/vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/s390x/hw_info.log": "CPU info:\nArchitecture:        s390x\nCPU op-mode(s):      32-bit, 64-bit\nByte Order:          Big Endian\nCPU(s):              4\nOn-line CPU(s) list: 0-3\nThread(s) per core:  1\nCore(s) per socket:  1\nSocket(s) per book:  1\nBook(s) per drawer:  1\nDrawer(s):           4\nNUMA node(s):        1\nVendor ID:           IBM/S390\nMachine type:        2964\nCPU dynamic MHz:     5000\nCPU static MHz:      5000\nBogoMIPS:            3033.00\nHypervisor:          z/VM 6.4.0\nHypervisor vendor:   IBM\nVirtualization type: full\nDispatching mode:    horizontal\nL1d cache:           128K\nL1i cache:           96K\nL2d cache:           2048K\nL2i cache:           2048K\nL3 cache:            65536K\nL4 cache:            491520K\nNUMA node0 CPU(s):   0-3\nFlags:               esan3 zarch stfle msa ldisp eimm dfp edat etf3eh highgprs te vx sie\n\n\nMemory:\n              total        used        free      shared  buff/cache   available\nMem:       16284748      632200    13382456       37940     2270092    15426604\nSwap:      16777212      354700    16422512\n\n\nStorage:\nFilesystem                Size  Used Avail Use% Mounted on\n/dev/mapper/system-build  118G  2.8G  115G   3% /mnt/build\n",
            "http://download.devel.redhat.com/brewroot/vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/x86_64/hw_info.log": "CPU info:\nArchitecture:        x86_64\nCPU op-mode(s):      32-bit, 64-bit\nByte Order:          Little Endian\nCPU(s):              24\nOn-line CPU(s) list: 0-23\nThread(s) per core:  2\nCore(s) per socket:  6\nSocket(s):           2\nNUMA node(s):        2\nVendor ID:           GenuineIntel\nCPU family:          6\nModel:               63\nModel name:          Intel(R) Xeon(R) CPU E5-2643 v3 @ 3.40GHz\nStepping:            2\nCPU MHz:             3646.839\nCPU max MHz:         3700.0000\nCPU min MHz:         1200.0000\nBogoMIPS:            6799.47\nVirtualization:      VT-x\nL1d cache:           32K\nL1i cache:           32K\nL2 cache:            256K\nL3 cache:            20480K\nNUMA node0 CPU(s):   0,2,4,6,8,10,12,14,16,18,20,22\nNUMA node1 CPU(s):   1,3,5,7,9,11,13,15,17,19,21,23\nFlags:               fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc cpuid aperfmperf pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm cpuid_fault epb invpcid_single pti ssbd ibrs ibpb stibp tpr_shadow vnmi flexpriority ept vpid ept_ad fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm ida arat pln pts md_clear flush_l1d\n\n\nMemory:\n              total        used        free      shared  buff/cache   available\nMem:       32624292      994276    17234720      886796    14395296    30267136\nSwap:      16482300      835572    15646728\n\n\nStorage:\nFilesystem                      Size  Used Avail Use% Mounted on\n/dev/mapper/rhel_x86--039-root  581G   15G  567G   3% /\n",
            "http://download.devel.redhat.com/brewroot/vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/i686/hw_info.log": "'CPU info:\nArchitecture:        i686\nCPU op-mode(s):      32-bit, 64-bit\nByte Order:          Little Endian\nCPU(s):              24\nOn-line CPU(s) list: 0-23\nThread(s) per core:  2\nCore(s) per socket:  6\nSocket(s):           2\nNUMA node(s):        2\nVendor ID:           GenuineIntel\nCPU family:          6\nModel:               63\nModel name:          Intel(R) Xeon(R) CPU E5-2643 v3 @ 3.40GHz\nStepping:            2\nCPU MHz:             2261.106\nCPU max MHz:         3700.0000\nCPU min MHz:         1200.0000\nBogoMIPS:            6799.88\nVirtualization:      VT-x\nL1d cache:           32K\nL1i cache:           32K\nL2 cache:            256K\nL3 cache:            20480K\nNUMA node0 CPU(s):   0,2,4,6,8,10,12,14,16,18,20,22\nNUMA node1 CPU(s):   1,3,5,7,9,11,13,15,17,19,21,23\nFlags:               fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc cpuid aperfmperf pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm cpuid_fault epb invpcid_single pti ssbd ibrs ibpb stibp tpr_shadow vnmi flexpriority ept vpid ept_ad fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm ida arat pln pts md_clear flush_l1d\n\n\nMemory:\n              total        used        free      shared  buff/cache   available\nMem:       32627392      974832    10973492      961680    20679068    30210696\nSwap:      16486396      783160    15703236\n\n\nStorage:\nFilesystem                      Size  Used Avail Use% Mounted on\n/dev/mapper/rhel_x86--037-root  581G   13G  569G   3% /\n",
        }
        return response_dict[url]

    @staticmethod
    def text():
        """
        overrides response.text() return. Returns hw_info.log text for
        host 94 build
        """
        return "CPU info:\nArchitecture:        ppc64le\nByte Order:          Little Endian\nCPU(s):              8\nOn-line CPU(s) list: 0-7\nThread(s) per core:  1\nCore(s) per socket:  8\nSocket(s):           1\nNUMA node(s):        1\nModel:               2.1 (pvr 004b 0201)\nModel name:          POWER8 (architected), altivec supported\nHypervisor vendor:   KVM\nVirtualization type: para\nL1d cache:           64K\nL1i cache:           32K\nNUMA node0 CPU(s):   0-7\n\n\nMemory:\n              total        used        free      shared  buff/cache   available\nMem:       24050560     1062144    16829376      158912     6159040    22675264\nSwap:      15744960       64000    15680960\n\n\nStorage:\nFilesystem             Size  Used Avail Use% Mounted on\n/dev/mapper/rhel-root  198G  6.3G  192G   4% /\n"


@pytest.fixture
def mock_session_response(monkeypatch):
    """
    Mocked responses for brew session for testing
    """

    def mock_list_channels(*args, **kwargs):
        """
        Covers default response of session.listChannels()
        """
        mockSession = MockSession()
        return mockSession.list_channels()

    def mock_get_build(build_id):
        """
        Covers session.getBuild
        """
        mockSession = MockSession()
        return mockSession.get_build(build_id)

    def mock_get_build_logs(build_id):
        """
        Covers session.getBuildLogs
        """
        mockSession = MockSession()
        return mockSession.get_build_logs(build_id)

    def mock_request_get(url):
        """
        Covers request.get("url")
        """
        # mockSession = MockSession()
        # return mockSession.requests_get(url)
        return MockSession()

    monkeypatch.setattr(session, "listChannels", mock_list_channels)
    monkeypatch.setattr(session, "getBuild", mock_get_build)
    monkeypatch.setattr(session, "getBuildLogs", mock_get_build_logs)
    monkeypatch.setattr(requests, "get", mock_request_get)


def test_collect_channels():
    """
    Tests for functioning of collect_channels function
    """
    channel_list = cv.collect_channels(MockSession())

    assert len(channel_list) == 37


def test_get_hw_info(mock_session_response, test_host_with_build):
    """
    Tests for functioning of collect_hw_info function
    """
    test_94_hw_dict = {
        "arches": "ppc64le",
        "CPU(s)": 8,
        "Ram": 24050560,
        "Disk": "198G",
        "Kernel": "4.18.0-193.28.1.el8_2.ppc64le",
        "Operating System": "RedHat 8.2",
    }
    my_host = test_host_with_build

    my_host.get_hw_info(MockSession())

    assert my_host.hw_dict == test_94_hw_dict


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
def mock_requests_get_log_dict():
    """
    Returns a dictionary of "url": "log string"
    Used to mock the requests.get("url") response for log collection tests
    """
    requests_log_dict = {
        "http://download.devel.redhat.com/brewroot/vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/aarch64/hw_info.log": "CPU info:\nArchitecture:        aarch64\nByte Order:          Little Endian\nCPU(s):              16\nOn-line CPU(s) list: 0-15\nThread(s) per core:  1\nCore(s) per cluster: 16\nSocket(s):           -\nCluster(s):          1\nNUMA node(s):        1\nVendor ID:           Cavium\nModel:               1\nModel name:          ThunderX2 99xx\nStepping:            0x1\nBogoMIPS:            400.00\nNUMA node0 CPU(s):   0-15\nFlags:               fp asimd evtstrm aes pmull sha1 sha2 crc32 atomics cpuid asimdrdm\n\n\nMemory:\n              total        used        free      shared  buff/cache   available\nMem:       16175168     1101376    12931904       71296     2141888    12707584\nSwap:       8392640      242304     8150336\n\n\nStorage:\nFilesystem             Size  Used Avail Use% Mounted on\n/dev/mapper/rhel-root  205G  5.9G  199G   3% /\n",
        "http://download.devel.redhat.com/brewroot/vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/ppc64le/hw_info.log": "CPU info:\nArchitecture:        ppc64le\nByte Order:          Little Endian\nCPU(s):              8\nOn-line CPU(s) list: 0-7\nThread(s) per core:  1\nCore(s) per socket:  8\nSocket(s):           1\nNUMA node(s):        1\nModel:               2.1 (pvr 004b 0201)\nModel name:          POWER8 (architected), altivec supported\nHypervisor vendor:   KVM\nVirtualization type: para\nL1d cache:           64K\nL1i cache:           32K\nNUMA node0 CPU(s):   0-7\n\n\nMemory:\n              total        used        free      shared  buff/cache   available\nMem:       24050560     1062144    16829376      158912     6159040    22675264\nSwap:      15744960       64000    15680960\n\n\nStorage:\nFilesystem             Size  Used Avail Use% Mounted on\n/dev/mapper/rhel-root  198G  6.3G  192G   4% /\n",
        "http://download.devel.redhat.com/brewroot/vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/s390x/hw_info.log": "CPU info:\nArchitecture:        s390x\nCPU op-mode(s):      32-bit, 64-bit\nByte Order:          Big Endian\nCPU(s):              4\nOn-line CPU(s) list: 0-3\nThread(s) per core:  1\nCore(s) per socket:  1\nSocket(s) per book:  1\nBook(s) per drawer:  1\nDrawer(s):           4\nNUMA node(s):        1\nVendor ID:           IBM/S390\nMachine type:        2964\nCPU dynamic MHz:     5000\nCPU static MHz:      5000\nBogoMIPS:            3033.00\nHypervisor:          z/VM 6.4.0\nHypervisor vendor:   IBM\nVirtualization type: full\nDispatching mode:    horizontal\nL1d cache:           128K\nL1i cache:           96K\nL2d cache:           2048K\nL2i cache:           2048K\nL3 cache:            65536K\nL4 cache:            491520K\nNUMA node0 CPU(s):   0-3\nFlags:               esan3 zarch stfle msa ldisp eimm dfp edat etf3eh highgprs te vx sie\n\n\nMemory:\n              total        used        free      shared  buff/cache   available\nMem:       16284748      632200    13382456       37940     2270092    15426604\nSwap:      16777212      354700    16422512\n\n\nStorage:\nFilesystem                Size  Used Avail Use% Mounted on\n/dev/mapper/system-build  118G  2.8G  115G   3% /mnt/build\n",
        "http://download.devel.redhat.com/brewroot/vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/x86_64/hw_info.log": "CPU info:\nArchitecture:        x86_64\nCPU op-mode(s):      32-bit, 64-bit\nByte Order:          Little Endian\nCPU(s):              24\nOn-line CPU(s) list: 0-23\nThread(s) per core:  2\nCore(s) per socket:  6\nSocket(s):           2\nNUMA node(s):        2\nVendor ID:           GenuineIntel\nCPU family:          6\nModel:               63\nModel name:          Intel(R) Xeon(R) CPU E5-2643 v3 @ 3.40GHz\nStepping:            2\nCPU MHz:             3646.839\nCPU max MHz:         3700.0000\nCPU min MHz:         1200.0000\nBogoMIPS:            6799.47\nVirtualization:      VT-x\nL1d cache:           32K\nL1i cache:           32K\nL2 cache:            256K\nL3 cache:            20480K\nNUMA node0 CPU(s):   0,2,4,6,8,10,12,14,16,18,20,22\nNUMA node1 CPU(s):   1,3,5,7,9,11,13,15,17,19,21,23\nFlags:               fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc cpuid aperfmperf pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm cpuid_fault epb invpcid_single pti ssbd ibrs ibpb stibp tpr_shadow vnmi flexpriority ept vpid ept_ad fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm ida arat pln pts md_clear flush_l1d\n\n\nMemory:\n              total        used        free      shared  buff/cache   available\nMem:       32624292      994276    17234720      886796    14395296    30267136\nSwap:      16482300      835572    15646728\n\n\nStorage:\nFilesystem                      Size  Used Avail Use% Mounted on\n/dev/mapper/rhel_x86--039-root  581G   15G  567G   3% /\n",
        "http://download.devel.redhat.com/brewroot/vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/i686/hw_info.log": "'CPU info:\nArchitecture:        i686\nCPU op-mode(s):      32-bit, 64-bit\nByte Order:          Little Endian\nCPU(s):              24\nOn-line CPU(s) list: 0-23\nThread(s) per core:  2\nCore(s) per socket:  6\nSocket(s):           2\nNUMA node(s):        2\nVendor ID:           GenuineIntel\nCPU family:          6\nModel:               63\nModel name:          Intel(R) Xeon(R) CPU E5-2643 v3 @ 3.40GHz\nStepping:            2\nCPU MHz:             2261.106\nCPU max MHz:         3700.0000\nCPU min MHz:         1200.0000\nBogoMIPS:            6799.88\nVirtualization:      VT-x\nL1d cache:           32K\nL1i cache:           32K\nL2 cache:            256K\nL3 cache:            20480K\nNUMA node0 CPU(s):   0,2,4,6,8,10,12,14,16,18,20,22\nNUMA node1 CPU(s):   1,3,5,7,9,11,13,15,17,19,21,23\nFlags:               fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc cpuid aperfmperf pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm cpuid_fault epb invpcid_single pti ssbd ibrs ibpb stibp tpr_shadow vnmi flexpriority ept vpid ept_ad fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm ida arat pln pts md_clear flush_l1d\n\n\nMemory:\n              total        used        free      shared  buff/cache   available\nMem:       32627392      974832    10973492      961680    20679068    30210696\nSwap:      16486396      783160    15703236\n\n\nStorage:\nFilesystem                      Size  Used Avail Use% Mounted on\n/dev/mapper/rhel_x86--037-root  581G   13G  569G   3% /\n",
    }
    return requests_log_dict


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
