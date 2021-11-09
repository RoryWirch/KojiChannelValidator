import json
import os


TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(TESTS_DIR, "fixtures")


class FakeCall:
    def __init__(self, name):
        self.name = name

    def __call__(self, *args, **kwargs):
        call_dirs = ["getBuildLogs", "getBuild"]
        if self.name in call_dirs:
            filename = str(args[0]) + ".json"
            fixture = os.path.join(FIXTURES_DIR, "calls", self.name, filename)
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


class FakeResponse:
    """Class to fake response"""

    def __init__(self, url):
        resp_dict = {
            "http://download.devel.redhat.com/brewroot/vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/aarch64/hw_info.log": "CPU info:\nArchitecture:        aarch64\nByte Order:          Little Endian\nCPU(s):              16\nOn-line CPU(s) list: 0-15\nThread(s) per core:  1\nCore(s) per cluster: 16\nSocket(s):           -\nCluster(s):          1\nNUMA node(s):        1\nVendor ID:           Cavium\nModel:               1\nModel name:          ThunderX2 99xx\nStepping:            0x1\nBogoMIPS:            400.00\nNUMA node0 CPU(s):   0-15\nFlags:               fp asimd evtstrm aes pmull sha1 sha2 crc32 atomics cpuid asimdrdm\n\n\nMemory:\n              total        used        free      shared  buff/cache   available\nMem:       16175168     1101376    12931904       71296     2141888    12707584\nSwap:       8392640      242304     8150336\n\n\nStorage:\nFilesystem             Size  Used Avail Use% Mounted on\n/dev/mapper/rhel-root  205G  5.9G  199G   3% /\n",
            "http://download.devel.redhat.com/brewroot/vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/ppc64le/hw_info.log": "CPU info:\nArchitecture:        ppc64le\nByte Order:          Little Endian\nCPU(s):              8\nOn-line CPU(s) list: 0-7\nThread(s) per core:  1\nCore(s) per socket:  8\nSocket(s):           1\nNUMA node(s):        1\nModel:               2.1 (pvr 004b 0201)\nModel name:          POWER8 (architected), altivec supported\nHypervisor vendor:   KVM\nVirtualization type: para\nL1d cache:           64K\nL1i cache:           32K\nNUMA node0 CPU(s):   0-7\n\n\nMemory:\n              total        used        free      shared  buff/cache   available\nMem:       24050560     1062144    16829376      158912     6159040    22675264\nSwap:      15744960       64000    15680960\n\n\nStorage:\nFilesystem             Size  Used Avail Use% Mounted on\n/dev/mapper/rhel-root  198G  6.3G  192G   4% /\n",
            "http://download.devel.redhat.com/brewroot/vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/s390x/hw_info.log": "CPU info:\nArchitecture:        s390x\nCPU op-mode(s):      32-bit, 64-bit\nByte Order:          Big Endian\nCPU(s):              4\nOn-line CPU(s) list: 0-3\nThread(s) per core:  1\nCore(s) per socket:  1\nSocket(s) per book:  1\nBook(s) per drawer:  1\nDrawer(s):           4\nNUMA node(s):        1\nVendor ID:           IBM/S390\nMachine type:        2964\nCPU dynamic MHz:     5000\nCPU static MHz:      5000\nBogoMIPS:            3033.00\nHypervisor:          z/VM 6.4.0\nHypervisor vendor:   IBM\nVirtualization type: full\nDispatching mode:    horizontal\nL1d cache:           128K\nL1i cache:           96K\nL2d cache:           2048K\nL2i cache:           2048K\nL3 cache:            65536K\nL4 cache:            491520K\nNUMA node0 CPU(s):   0-3\nFlags:               esan3 zarch stfle msa ldisp eimm dfp edat etf3eh highgprs te vx sie\n\n\nMemory:\n              total        used        free      shared  buff/cache   available\nMem:       16284748      632200    13382456       37940     2270092    15426604\nSwap:      16777212      354700    16422512\n\n\nStorage:\nFilesystem                Size  Used Avail Use% Mounted on\n/dev/mapper/system-build  118G  2.8G  115G   3% /mnt/build\n",
            "http://download.devel.redhat.com/brewroot/vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/x86_64/hw_info.log": "CPU info:\nArchitecture:        x86_64\nCPU op-mode(s):      32-bit, 64-bit\nByte Order:          Little Endian\nCPU(s):              24\nOn-line CPU(s) list: 0-23\nThread(s) per core:  2\nCore(s) per socket:  6\nSocket(s):           2\nNUMA node(s):        2\nVendor ID:           GenuineIntel\nCPU family:          6\nModel:               63\nModel name:          Intel(R) Xeon(R) CPU E5-2643 v3 @ 3.40GHz\nStepping:            2\nCPU MHz:             3646.839\nCPU max MHz:         3700.0000\nCPU min MHz:         1200.0000\nBogoMIPS:            6799.47\nVirtualization:      VT-x\nL1d cache:           32K\nL1i cache:           32K\nL2 cache:            256K\nL3 cache:            20480K\nNUMA node0 CPU(s):   0,2,4,6,8,10,12,14,16,18,20,22\nNUMA node1 CPU(s):   1,3,5,7,9,11,13,15,17,19,21,23\nFlags:               fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc cpuid aperfmperf pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm cpuid_fault epb invpcid_single pti ssbd ibrs ibpb stibp tpr_shadow vnmi flexpriority ept vpid ept_ad fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm ida arat pln pts md_clear flush_l1d\n\n\nMemory:\n              total        used        free      shared  buff/cache   available\nMem:       32624292      994276    17234720      886796    14395296    30267136\nSwap:      16482300      835572    15646728\n\n\nStorage:\nFilesystem                      Size  Used Avail Use% Mounted on\n/dev/mapper/rhel_x86--039-root  581G   15G  567G   3% /\n",
            "http://download.devel.redhat.com/brewroot/vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/i686/hw_info.log": "'CPU info:\nArchitecture:        i686\nCPU op-mode(s):      32-bit, 64-bit\nByte Order:          Little Endian\nCPU(s):              24\nOn-line CPU(s) list: 0-23\nThread(s) per core:  2\nCore(s) per socket:  6\nSocket(s):           2\nNUMA node(s):        2\nVendor ID:           GenuineIntel\nCPU family:          6\nModel:               63\nModel name:          Intel(R) Xeon(R) CPU E5-2643 v3 @ 3.40GHz\nStepping:            2\nCPU MHz:             2261.106\nCPU max MHz:         3700.0000\nCPU min MHz:         1200.0000\nBogoMIPS:            6799.88\nVirtualization:      VT-x\nL1d cache:           32K\nL1i cache:           32K\nL2 cache:            256K\nL3 cache:            20480K\nNUMA node0 CPU(s):   0,2,4,6,8,10,12,14,16,18,20,22\nNUMA node1 CPU(s):   1,3,5,7,9,11,13,15,17,19,21,23\nFlags:               fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc cpuid aperfmperf pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm cpuid_fault epb invpcid_single pti ssbd ibrs ibpb stibp tpr_shadow vnmi flexpriority ept vpid ept_ad fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm ida arat pln pts md_clear flush_l1d\n\n\nMemory:\n              total        used        free      shared  buff/cache   available\nMem:       32627392      974832    10973492      961680    20679068    30210696\nSwap:      16486396      783160    15703236\n\n\nStorage:\nFilesystem                      Size  Used Avail Use% Mounted on\n/dev/mapper/rhel_x86--037-root  581G   13G  569G   3% /\n",
        }

        self.text = resp_dict[url]
