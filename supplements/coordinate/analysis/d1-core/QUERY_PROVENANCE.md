# Fresh-query provenance

Queries were executed on 2026-09-27 through Wolfram's networked environment because the local container could not resolve external DNS.

## ESA Gaia TAP

Endpoint: `https://gea.esac.esa.int/tap-server/tap/sync`

ADQL:

```sql
SELECT source_id,ra,dec,pmra,pmdec,parallax,radial_velocity,ref_epoch
FROM gaiadr3.gaia_source
WHERE source_id IN (
3496509309189181184,4843191593270342656,4649396037451459712,
2660349163149053824,3190232820489766656,2956570141274256512,
2644370304260053376,2437221214075471744,3854090071297359616,
651765552072217216)
```

Returned values are preserved in `fresh_gaia_tap_2026-09-27.csv`.

## SIMBAD TAP

Endpoint: `https://simbad.cds.unistra.fr/simbad/sim-tap/sync`

The exact Gaia DR3 identifiers were queried against `ident` joined to `basic`, returning A-G and no rows for H-J. Independent 10-arcsec cone queries around H-J returned no astronomical object. Results are preserved in `fresh_simbad_tap_2026-09-27.csv`.

SIMBAD documentation states that its default coordinate epoch is J2000 and that identifier coordinates use ICRS, J2000, equinox 2000. SIMBAD proper-motion RA is the `mu_alpha cos(delta)` quantity.
