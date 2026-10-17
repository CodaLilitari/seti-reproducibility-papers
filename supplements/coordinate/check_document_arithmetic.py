#!/usr/bin/env python3
"""Check documentary summaries from frozen tables. No network or scientific pipeline replay.
Usage: python check_document_arithmetic.py [BUNDLE_DIRECTORY]
"""
from __future__ import annotations
import csv, json, math, sys
from pathlib import Path

def main(root: Path) -> dict:
    def rows(rel):
        with (root/rel).open(encoding='utf-8-sig',newline='') as h:return list(csv.DictReader(h))
    def close(a,b,tol=1e-9):
        if not math.isclose(a,b,rel_tol=tol,abs_tol=tol):raise ValueError((a,b))
    allrows=rows('support/astrometry/rowwise_offsets.csv')
    groups={'AF':[r for r in allrows if r['branch']=='WISE' and r['candidate'] in 'ABCDEF'],
            'HJ':[r for r in allrows if r['branch']=='WISE' and r['candidate'] in 'HIJ'],
            'radio':[r for r in allrows if r['branch']!='WISE']}
    expected={'AF':(24,3,24),'HJ':(12,12,1),'radio':(7,7,1)}
    summaries={}
    for name,g in groups.items():
        counts=(len(g),sum(abs(float(r['residual_stated_arcsec']))<.05 for r in g),sum(abs(float(r['residual_minus16_arcsec']))<.05 for r in g))
        if counts!=expected[name]:raise ValueError((name,counts))
        summaries[name]={'n':counts[0],'match_at_stated_epoch':counts[1],'match_minus16':counts[2],
                         'mae_stated':sum(abs(float(r['residual_stated_arcsec'])) for r in g)/len(g),
                         'mae_minus16':sum(abs(float(r['residual_minus16_arcsec'])) for r in g)/len(g)}
    controls=rows('support/astrometry/A_controls_transcribed.csv');scales={}
    for i,n,expected_scale in [(1,15,.174470628),(2,15,.212924087),(3,15,1.501048522),(4,9,3.287614806)]:
        vals=[float(r[f'w{i}_offset_arcsec']) for r in controls if r[f'w{i}_offset_arcsec']]
        if len(vals)!=n:raise ValueError('wrong control count')
        s=math.sqrt(sum(x*x for x in vals)/(2*n));close(s,expected_scale);scales[f'W{i}']={'n':n,'scale':s}
    probabilities={}
    for r in rows('support/astrometry/conditional_probabilities.csv'):
        p=math.exp(-float(r['correct_date_offset_arcsec'])**2/(2*float(r['published_scale_arcsec'])**2))
        close(p,float(r['conditional_p_fixed_published_scale']));probabilities[r['candidate']+' '+r['band']]=p
    rs=rows('support/ren2024/math/seven_rows.csv');tab=rows('support/ren2024/EPOCH_UNCERTAINTY_TABLE.csv')
    if len(rs)!=7 or len(tab)!=7:raise ValueError('seven rows required')
    seven=[]
    for r,t in zip(rs,tab):
        if (r['candidate'],r['survey'])!=(t['candidate'],t['survey']):raise ValueError('identity order')
        for key,val in r.items():
            if key in t and val!=t[key]:raise ValueError(('table mismatch',key))
        seven.append({k:(float(r[k]) if r[k] else None) for k in ['native_J2000_radius_arcsec','native_proxy_radius_arcsec','native_support_radius_min_arcsec','native_support_radius_max_arcsec']})
    a=rs[0]
    close(float(a['native_J2000_radius_arcsec']),4.877314668883262)
    close(float(a['native_proxy_radius_arcsec']),3.2940573080944358)
    width=float(a['native_support_radius_max_arcsec'])-float(a['native_support_radius_min_arcsec'])
    tgss=json.loads((root/'support/ren2024/math/tgss_reference_diagnostic.json').read_text())
    norm=math.hypot(*tgss['printed_components_arcsec'])
    close(norm,5.498791503594221)
    irr=math.hypot(*tgss['joint_fit_computed_minus_printed_components_arcsec'])
    close(irr,tgss['irreducible_component_residual_norm_arcsec'])
    if any(r['common_epoch_exists'] for r in tgss['rounding_feasibility']):raise ValueError('unexpected feasible TGSS common epoch')
    density=1/(31*3600**2);factor=9e-6/density;overlap=5_000_000*math.pi*10**2*density
    close(density,2.4890481879729194e-9);close(factor,3615.84);close(overlap,3.90978775,tol=2e-9)
    rhos=rows('support/ren2024/math/reviewer_followup_finite_rho.csv')
    vals=[float(r['D_conditional']) for r in rhos if r['ra_error_convention']=='ra_coordinate_arcsec' and float(r['additional_stochastic_isotropic_sigma_arcsec'])==0]
    for got,exp in zip(vals,[3.548636973325912,2.524157,2.097019]):close(got,exp,tol=5e-7)
    return {'scope':'Documentary arithmetic and stored-table consistency only; no new astrometry, covariance optimization, FITS extraction, source query or full-science replay.',
            'status':'pass','branch_summaries':summaries,'recovered_A_scales':scales,'fixed_scale_diagnostics':probabilities,
            'seven_row_native_values':seven,'A_epoch_envelope_width_arcsec':width,
            'TGSS_printed_component_norm_arcsec':norm,'TGSS_joint_residual_norm_arcsec':irr,
            'density_arcsec_minus2':density,'printed_density_factor':factor,'illustrative_expected_aperture_overlaps':overlap,
            'A_stored_finite_rho_D':vals}
if __name__=='__main__':
    try:print(json.dumps(main(Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent),indent=2,allow_nan=False))
    except (OSError,ValueError,KeyError) as exc:raise SystemExit(f'CHECK FAILED: {exc}')
