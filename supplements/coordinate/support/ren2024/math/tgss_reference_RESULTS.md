# TGSS single-stellar-epoch diagnostic

For the same Gaia star under linear proper motion, changing only one common stellar epoch cannot reproduce both printed TGSS components at their stated rounding.

| Diagnostic | Result |
|---|---:|
| East-only effective epoch | J1999.999536685 |
| North-only effective epoch | J2020.139022842 |
| Best joint unweighted epoch | J2010.517090141 |
| Joint computed-minus-printed east residual | 0.499425982 arcsec |
| Joint computed-minus-printed north residual | -0.477686712 arcsec |
| Irreducible joint residual norm | 0.691093993 arcsec |
| Printed radius | 5.499000 arcsec |
| Norm of printed components | 5.498791504 arcsec |
| Same-J2000-reference spherical radius | 5.773403119 arcsec |

The printed radius is consistent with its printed components at rounding. Those components cannot both come from a single different epoch of this star. The separately allowed east and north epoch intervals remain disjoint even after including half of the last printed digit in radio RA (0.0005 seconds of time), radio declination (0.0005 arcsec), and the components (0.0005 arcsec each). The exact intervals are in the JSON.

This is a conditional compatibility calculation for the supplied central Gaia motion, not a probability or significance calculation. It does not exclude another star, mixed fields, a different reference coordinate, transcription, or another workflow error, and does not identify the authors' historical cause. Native TGSS declination remains unchanged.

Independent checks cover implied-coordinate inversion, analytic orthogonal projection, scalar minimization, a separate coarse scan, rounding-feasible interval intersection, component/radius consistency and preservation of all already reviewed math files. All 17 recorded checks passed.
