"""Serial, offline replay of the immutable delivered TESS development package."""
from __future__ import annotations
import os
for _key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS'):
    os.environ[_key] = '1'
import contextlib, ctypes, hashlib, importlib, io, json, platform, runpy, shutil, sys, time, unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent/'source'/'planet_hunt_tess_development_2026-10-08'
COPY = ROOT/'package_copy'

def block_network(event, args):
    if event in ('socket.connect','socket.connect_ex','socket.getaddrinfo','socket.bind','socket.sendto'):
        raise RuntimeError('Offline replay blocks network: '+event)
sys.addaudithook(block_network)
sys.dont_write_bytecode = True
if os.name == 'nt':
    ctypes.windll.kernel32.GetCurrentProcess.restype=ctypes.c_void_p
    ctypes.windll.kernel32.SetPriorityClass.argtypes=[ctypes.c_void_p,ctypes.c_ulong]
    ctypes.windll.kernel32.GetPriorityClass.argtypes=[ctypes.c_void_p]
    _process=ctypes.windll.kernel32.GetCurrentProcess()
    if not ctypes.windll.kernel32.SetPriorityClass(_process,0x4000) or ctypes.windll.kernel32.GetPriorityClass(_process)!=0x4000:
        raise RuntimeError('Could not establish below-normal Windows priority')

def verify_manifest(path):
    rows = json.loads((path/'MANIFEST.json').read_text())
    failed = []
    for row in rows:
        data = (path/row['path']).read_bytes()
        if len(data) != row['bytes'] or hashlib.sha256(data).hexdigest() != row['sha256']:
            failed.append(row['path'])
    return {'entries':len(rows),'failures':failed}

def memory_peak():
    if os.name != 'nt':
        return None
    class PMC(ctypes.Structure):
        _fields_ = [('cb',ctypes.c_ulong),('PageFaultCount',ctypes.c_ulong)]+[(n,ctypes.c_size_t) for n in ('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage')]
    ctypes.windll.kernel32.GetCurrentProcess.restype=ctypes.c_void_p
    ctypes.windll.psapi.GetProcessMemoryInfo.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_ulong]
    info=PMC();info.cb=ctypes.sizeof(info)
    ok=ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.windll.kernel32.GetCurrentProcess(),ctypes.byref(info),info.cb)
    return int(info.PeakWorkingSetSize) if ok else None

def main():
    started=time.perf_counter()
    if COPY.exists():
        raise RuntimeError('Refusing to overwrite a previous replay copy')
    original_before=verify_manifest(SOURCE)
    assert not original_before['failures'],original_before
    shutil.copytree(SOURCE,COPY)
    sys.path.insert(0,str(COPY))
    with (ROOT/'manifest_verification.log').open('w') as log,contextlib.redirect_stdout(log):
        runpy.run_path(str(COPY/'verify.py'),run_name='__main__')
    with (ROOT/'six_tests.log').open('w') as log:
        tests=unittest.defaultTestLoader.loadTestsFromName('test_search')
        result=unittest.TextTestRunner(stream=log,verbosity=2).run(tests)
    if not result.wasSuccessful():
        raise RuntimeError('Original implementation tests failed')
    search=importlib.import_module('search')
    with (ROOT/'three_peaks.log').open('w') as log,contextlib.redirect_stdout(log):
        search.main()
    baseline=json.loads((SOURCE/'results/search_results.json').read_text())
    replay=json.loads((COPY/'results/search_results.json').read_text())
    comparisons=[]
    for old,new in zip(baseline['peaks'],replay['peaks']):
        comparisons.append({'iteration':new['iteration'],'period_days':new['period_days'],
            'depth_ppm':new['depth_ppm'],'sap_depth_same_box_ppm':new['sap_depth_same_box_ppm'],
            'period_delta_days':new['period_days']-old['period_days'],
            'pdc_depth_delta_ppm':new['depth_ppm']-old['depth_ppm'],
            'sap_depth_delta_ppm':new['sap_depth_same_box_ppm']-old['sap_depth_same_box_ppm'],
            'populated_events':new['populated_events'],'bins_per_event':new['bins_per_event']})
    original_after=verify_manifest(SOURCE)
    import numpy as np
    receipt={'generated_utc':datetime.now(timezone.utc).isoformat(),'python':sys.version,'executable':sys.executable,
        'platform':platform.platform(),'numpy':np.__version__,'thread_limits':{k:os.environ[k] for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS')},
        'network':'socket connections, DNS, bind and sendto blocked by audit hook','priority':'Windows BELOW_NORMAL_PRIORITY_CLASS',
        'source_manifest_before':original_before,'source_manifest_after':original_after,
        'tests':{'run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped)},
        'original_config_unchanged':baseline['config']==replay['config'],'peak_comparisons':comparisons,
        'peak_working_set_bytes':memory_peak(),'elapsed_seconds':time.perf_counter()-started,
        'scope':'Lossy 30-minute original development replay only; no new target or astronomical validation'}
    (ROOT/'replay_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__': main()
