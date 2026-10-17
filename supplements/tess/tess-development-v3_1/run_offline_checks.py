"""One-thread, network-blocked v3.1 synthetic verification and connected example."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS'):os.environ[key]='1'
import sys,ctypes,json,unittest,time,hashlib,platform
from pathlib import Path
from datetime import datetime,timezone
sys.dont_write_bytecode=True
def guard(event,args):
    if event in ('socket.connect','socket.connect_ex','socket.getaddrinfo','socket.bind','socket.sendto'):raise RuntimeError('Synthetic checks forbid network')
sys.addaudithook(guard)
if os.name=='nt':
    k=ctypes.windll.kernel32;k.GetCurrentProcess.restype=ctypes.c_void_p;k.SetPriorityClass.argtypes=[ctypes.c_void_p,ctypes.c_ulong];k.GetPriorityClass.argtypes=[ctypes.c_void_p]
    handle=k.GetCurrentProcess()
    if not k.SetPriorityClass(handle,0x4000) or k.GetPriorityClass(handle)!=0x4000:raise RuntimeError('Could not verify below-normal priority')

def peak_memory():
    class P(ctypes.Structure):
        _fields_=[('cb',ctypes.c_ulong),('faults',ctypes.c_ulong)]+[(name,ctypes.c_size_t) for name in ['peak','current','pp','p','pn','n','pf','ppf']]
    p=P();p.cb=ctypes.sizeof(p);ctypes.windll.psapi.GetProcessMemoryInfo.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_ulong]
    if not ctypes.windll.psapi.GetProcessMemoryInfo(handle,ctypes.byref(p),p.cb):raise RuntimeError('Memory measurement failed')
    return int(p.peak)

def main():
    root=Path(__file__).resolve().parent;start=time.monotonic();identity=lambda:{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.glob('*.py')}
    before=identity()
    with (root/'unittest.log').open('w') as log:
        result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.discover(str(root),pattern='test_*.py'))
    from synthetic_driver import run_driver
    frozen,summary=run_driver(root/'synthetic_output')
    import numpy,scipy,astropy
    from scipy.special import ndtr
    from tess_components import grid_plan,holdout_decision
    diagnostic_examples={}
    for name,depths in [('diffuse',[-.1]+[2.2]*9),('concentrated',[-.1,19.72]+[.01]*8),('zero',[0.,0.])]:
        diagnostic_examples[name]=holdout_decision({'depth':1.97 if name!='zero' else 0.,'variance':.01},
            [{'covered':True,'depth':depth,'variance':1.} for depth in depths])
    peak=peak_memory() if os.name=='nt' else None
    receipt={'utc':datetime.now(timezone.utc).isoformat(),'scope':'Offline synthetic development only; no unfamiliar metadata/flux or server probes',
        'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),
        'successful':result.wasSuccessful(),'source_unchanged_during_run':before==identity(),'source_sha256':before,
        'python':sys.version,'executable':sys.executable,'packages':{'numpy':numpy.__version__,'scipy':scipy.__version__,'astropy':astropy.__version__},
        'network_guard':'socket/DNS/bind/sendto blocked','numerical_threads':1,'windows_priority_verified':'BELOW_NORMAL_PRIORITY_CLASS' if os.name=='nt' else None,
        'peak_working_set_bytes':peak,'elapsed_seconds':time.monotonic()-start,
        'phi_1_power_25':float(ndtr(1)**25),'730_day_grid_plan':grid_plan(730.),
        'connected_holdout_status':summary['holdout']['status'],'connected_freeze_sha256':frozen['sha256'],
        'base_v3_manifest_sha256':'89eacdaf36a78fafd517c000af9696363fa754fbb0936d9ad8fe415a469114f8',
        'contribution_diagnostic_examples':diagnostic_examples}
    (root/'VERIFICATION_RECEIPT.json').write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
    print(json.dumps(receipt,indent=2,allow_nan=False))
    if not result.wasSuccessful() or before!=identity() or (peak is not None and peak>=1024**3):raise SystemExit(1)

if __name__=='__main__':main()
