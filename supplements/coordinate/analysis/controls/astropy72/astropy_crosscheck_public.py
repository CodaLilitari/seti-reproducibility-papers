"""Separate Astropy propagation and spherical-separation verification.

Requires astropy==8.0.1; does not import the stdlib calculation code.
The Gaia snapshot remains the one obtained on 2026-09-25.
"""
from pathlib import Path
import csv,json,hashlib,sys,platform
import astropy
import numpy
from astropy.coordinates import SkyCoord,Distance
from astropy.time import Time
import astropy.units as u
from astropy.utils import iers

iers.conf.auto_download = False

BASE=Path(__file__).resolve().parent
GAIA=BASE/'inputs/gaia_dr3_snapshot_20260925.csv'
assert hashlib.sha256(GAIA.read_bytes()).hexdigest()=='ebc0f022f36d65525a96082be2c9b7d96302e17f24a02276af50a5fc70dd5c8b'
assert hashlib.sha256((BASE/'source_tables.json').read_bytes()).hexdigest()=='62a9fe9430be1d0b9ff0e85549ae002a7c565be1239f3994dc7ddf2b41490396'
assert hashlib.sha256((BASE/'candidate_radius_models.csv').read_bytes()).hexdigest()=='846bffa0d5a7f084f22fb2c9c74b0a04201a522b89ff3ea32b22ee710a6f2eab'
tables=json.loads((BASE/'source_tables.json').read_text(encoding='utf8'))
gaia={r['source_id']:r for r in csv.DictReader(GAIA.open())}
stdlib={(r['candidate'],r['band']):r for r in csv.DictReader((BASE/'candidate_radius_models.csv').open())}
stars={}
for r in tables['S2.T1'][1:]:
    g=gaia[r[1]]
    pos=SkyCoord(ra=float(g['ra'])*u.deg,dec=float(g['dec'])*u.deg,
                 pm_ra_cosdec=float(g['pmra'])*u.mas/u.yr,
                 pm_dec=float(g['pmdec'])*u.mas/u.yr,
                 distance=Distance(parallax=float(g['parallax'])*u.mas),
                 radial_velocity=0*u.km/u.s,
                 obstime=Time(float(g['ref_epoch']),format='jyear'),frame='icrs')
    stars[r[0][0]]=(pos,float(r[9]),float(r[10]))
out=[]
for tid,letters in [('S3.T4','AB'),('S3.T5','CDEF'),('S3.T6','HIJ')]:
    rows=[r for r in tables[tid] if len(r)>5 and r[1] in ('W1','W2','W3','W4')]
    for i,r in enumerate(rows):
        letter=letters[i//4];band=r[1]
        centroid=SkyCoord(r[2],r[3].replace('\\',' '),unit=(u.hourangle,u.deg),frame='icrs')
        pos,epoch12,epoch34=stars[letter];epoch=epoch12 if band in ('W1','W2') else epoch34
        for label,shift in [('correct_2016',0),('offset_minus16',-16)]:
            moved=pos.apply_space_motion(new_obstime=Time(epoch+shift,format='jyear'))
            radius=centroid.separation(moved).to_value(u.arcsec)
            reference=float(stdlib[(letter,band)]['r_'+label])
            out.append({'candidate':letter,'band':band,'model':label,'epoch':epoch+shift,
                        'astropy_radius_arcsec':radius,'stdlib_radius_arcsec':reference,
                        'astropy_minus_stdlib_arcsec':radius-reference})
assert len(out)==72 and len({(r['candidate'],r['band']) for r in out})==36
max_abs=max(abs(r['astropy_minus_stdlib_arcsec']) for r in out)
# The two methods need not be exactly equal: full space motion follows the
# celestial sphere, while the independently derived stdlib calculation is linear
# in RA/Dec. Require agreement comfortably finer than the printing precision.
assert max_abs<1e-4, 'Astropy crosscheck exceeded 0.1 mas tolerance'
with (BASE/'astropy_crosscheck.csv').open('w',newline='',encoding='utf8') as f:
    w=csv.DictWriter(f,fieldnames=out[0]);w.writeheader();w.writerows(out)
summary={'astropy':astropy.__version__,'numpy':numpy.__version__,'python':sys.version,
         'executable':sys.executable,'platform':platform.platform(),
         'gaia_snapshot_date':'2026-09-25','rows':len(out),'candidates_bands':36,
         'max_absolute_difference_arcsec':max_abs,
         'max_absolute_difference_by_model_arcsec':{
             m:max(abs(r['astropy_minus_stdlib_arcsec']) for r in out if r['model']==m)
             for m in ('correct_2016','offset_minus16')},
         'accepted_tolerance_arcsec':1e-4,
         'method':'SkyCoord parses sexagesimal strings; distance from parallax; radial velocity assumed zero; apply_space_motion from Gaia reference epoch; spherical separation. No stdlib audit functions imported.',
         'limitations':'Checks propagation arithmetic under zero radial velocity; not new observations, fresh Gaia retrieval, or original-code recovery.'}
(BASE/'astropy_crosscheck_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
print(json.dumps(summary,indent=2))
