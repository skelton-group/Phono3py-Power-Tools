# phono3py-isotopes
----------

`phono3py-isotopes` is a simple script to generate input parameters to simulate the effect of mass variation at atomic sites in the input crystal structure on the lattice thermal conductivity <i>&kappa;</i><sub>latt</sub> in Phono3py calculations.


## Theory
----------

The (average) mass of the atoms <i>m</i><sub>ave</sub> directly affects the phonon frequencies <i>&omega;<sub>&lambda;</sub></i> *via* the dynamical matrix ***D***(**q**), and also appears in the expression for the three-phonon interaction strengths <i>P<sub>&lambda;</sub></i> used to calculate the linewidths &Gamma;<sub><i>&lambda;</i></sub>.
More details and formulae can be found in [Ref. 1](#Ref1).

In Phono3py, the average mass at the atomic sites in the input structure can be set using the `--mass` tag or corresponding `MASS` settings tag.
For sites with *i* isotopes with abundance <i>a<sub>i</sub></i> and mass <i>m<sub>i</sub></i>, <i>m</i><sub>ave</sub> is calculated as:

<br>
<img src="Resources/phono3py-isotopes_Equation1.png" alt="phono3py-isotopes_Equation1.png">
<br>

The natural variation in atomic mass due to the presence of elemental isotopes with different masses can introduce additional "isotope scattering" and thus reduce <i>&kappa;</i><sub>latt</sub>.
In Phono3py, isotope effects can be included using the model in [Ref. 2](#Ref2).
The required parameter is the "mass variance" <i>m></i><sub>var</sub>, calculated using the formula:

<br>
<img src="Resources/phono3py-isotopes_Equation2.png" alt="phono3py-isotopes_Equation2.png">
<br>

The mass variance at the atomic sites can be set using the `--mass-variances`/`--mv` command-line parameters or the corresponding `MASS_VARIANCES` tag.


## Installation and requirements
----------

No installation is necessary, but you may add the script folder to your `$PATH` variable if you wish - e.g.:

```bash
export PATH=${PATH}:/mnt/d/Repositories/Phono3py-Tools
```

The main `phono3py-isotopes` reads isotope data from the Phonopy database and therefore requires the `phonopy` Python library to be installed.


## Brief tutorial
----------


### a. Natural isotopic abundance <a name="Tutorial.A"></a>

To obtain the appropriate `--mass` and `--mass-variances` tags to input the natural isotopic mass variance into Phono3py, simply run `phono3py-isotopes` with the list of atoms in the crystal structure (in site order):

```bash
$ phono3py-isotopes Ga As
```

The program prints for each atomic site a list of isotopes with their abundance and mass, followed by the average mass and mass variance.
The `--mass` and `--mass-variances` tags to input into Phono3py are then printed at the end of the output.

```
Site 1 (Ga)
-----------

  69_Ga   : a_i =  60.11 %, m_i =   68.92558
  71_Ga   : a_i =  39.89 %, m_i =   70.92471

  m_ave = 69.72307
  m_var = 1.97127e-04


Site 2 (As)
-----------

  75_As   : a_i = 100.00 %, m_i =   74.92160

  m_ave = 74.92160
  m_var = 0.00000e+00


To input this data into Phono3py:
---------------------------------
  --mass="69.72307 74.92160"
  --mass-variances="1.97127e-04 0.00000e+00"
```

We can now perform Phono3py calculations with and without the mass variance:

```bash
$ phono3py --dim="2 2 2" --dim-fc2="3 3 3" --pa="0 1/2 1/2  1/2 0 1/2  1/2 1/2 0" \
    --fc2 --fc3 -v --br --mesh="32 32 32"
```

```bash
$ phono3py --dim="2 2 2" --dim-fc2="3 3 3" --pa="0 1/2 1/2  1/2 0 1/2  1/2 1/2 0" \
    --fc2 --fc3 -v --br --mesh="32 32 32" --read-gamma \
	--mass="69.72307 74.92160" --mass-variances="1.97127e-04 0.00000e+00" -o "iso.nat.a"
```

This example is somewhat contrived, as (a) the atomic masses used are the Phono3py defaults, so do not need to be set, and (b) the natural isotopic mass variance can be set automatically using the `--isotope` tag:

```
$ phono3py --dim="2 2 2" --dim-fc2="3 3 3" --pa="0 1/2 1/2  1/2 0 1/2  1/2 1/2 0" \
    --fc2 --fc3 -v --br --mesh="32 32 32" --read-gamma --isotope -o "iso.nat.b"
```

As expected, the last two commands give practically the same result.*

<table>
  <tr>
    <th rowspan="2" style="vertical-align:bottom;">Calc.</th>
    <th colspan="2"><i>&kappa;</i><sub>latt</sub> [W m<sup>-1</sup> K<sup>-1</sup>]</th>
  </tr>
 <tr>
    <th><i>T</i> = 100 K</th>
    <th><i>T</i> = 300 K</th>
  </tr>
  <tr>
    <td>No Iso.</td>
    <td>158.9</td>
    <td>37.89</td>
  </tr>
  <tr>
    <td>Nat. Iso. (1)</td>
    <td>144.6</td>
    <td>36.90</td>
  </tr>
  <tr>
    <td>Nat. Iso. (2)</td>
    <td>144.6</td>
    <td>36.90</td>
  </tr>
</table>

<img src="Resources/phono3py-isotopes_TutorialA.png" alt="phono3py-isotopes_TutorialA.png" width="750">

\* The results are not _exactly_ the same.
This is because Phonopy has two different databases - a list of average masses, and a higher-precision list of isotopes used to calculate mass variance parameters for the `--isotope` tag.
`phono3py-isotopes` uses the latter database for both, so the masses specified in the `--mass` tag will generally be slightly different from the defaults.
In practice, the differences in the calculated <i>&kappa;</i><sub>latt</sub> are negligably small.


### b. Site mass disorder <a name="Tutorial.B"></a>

Suppose we replaced 1 % of the As with P.
The effect of this doping/alloying on the thermal transport can be modelled approximately* by changing the average mass and mass variance at the anion site.
The appropriate `--mass` and `--mass-variances` tags to input this into Phono3py can be generated with `phono3py-isotopes` using the `--site-average` flag.

```bash
$ phono3py-isotopes Ga, As P --site-average --site-occupation="1.0, 0.99 0.01"
```

The comma in the list of atomic symbols delineates atoms at the two atomic sites.
A corresponding list of site occupation fractions is also set with the `--site-occupation` parameter.
Note that `phono3py-isotopes` automatically includes the natural isotopic mass variation when calculating the average masses and mass variance for the mixed sites.

Running the command above produces the following output:

```
Site 1 (Ga)
-----------

  69_Ga   : a_i =  60.11 %, m_i =   68.92558
  71_Ga   : a_i =  39.89 %, m_i =   70.92471

  m_ave = 69.72307
  m_var = 1.97127e-04


Site 2 (As, P)
--------------

  75_As   : a_i =  99.00 %, m_i =   74.92160
  31_P    : a_i =   1.00 %, m_i =   30.97376

  m_ave = 74.48212
  m_var = 3.44672e-03


To input this data into Phono3py:
---------------------------------
  --mass="69.72307 74.48212"
  --mass-variances="1.97127e-04 3.44672e-03"
```

We can now input these `--mass` and `--mass-variances` parameters into Phono3py:

```bash
$ phono3py --dim="2 2 2" --dim-fc2="3 3 3" --pa="0 1/2 1/2  1/2 0 1/2  1/2 1/2 0" \
    --fc2 --fc3 -v --br --mesh="32 32 32" \
    --mass="69.72307 74.48212" --mass-variances="1.97127e-04 3.44672e-03" -o "As99-P1" 
```

Note that we did not use the `--read-gamma` tag as in the previous example.
The doping changes the average mass as well as the mass variance, which will in turn affect the phonon spectrum and the linewidths.

<table>
  <tr>
    <th rowspan="2" style="vertical-align:bottom;">Calc.</th>
    <th colspan="2"><i>&kappa;</i><sub>latt</sub> [W m<sup>-1</sup> K<sup>-1</sup>]</th>
  </tr>
 <tr>
    <th><i>T</i> = 100 K</th>
    <th><i>T</i> = 300 K</th>
  </tr>
  <tr>
    <td>GaAs</td>
    <td>144.6</td>
    <td>36.90</td>
  </tr>
  <tr>
    <td>Ga(As<sub>0.99</sub>P<sub>0.01</sub>)</td>
    <td>81.53</td>
    <td>28.99</td>
  </tr>
</table>

<img src="Resources/phono3py-isotopes_TutorialB.png" alt="phono3py-isotopes_TutorialB.png" width="750">

\* This procedure is approximate because it does not account for changes in the 2<sup>nd</sup>- and 3<sup>rd</sup>-order force constants due to differences in chemical bonding and/or changes in cell volume - more accurate predictions for homogeneous alloys might be obtained using a virtual crystal approximation (VCA) such as that implemented in [almaBTE](#Ref3).


### c. Specific isotope ratios <a name="Tutorial.C"></a>

The `--site-average` option can also be used to set up calculations for specific isotopic ratios.

Running the script to prepare data as in the first example lists the natural abundances and masses of the two isotopes of Ga:

```bash
$ phono3py-isotopes Ga As
```

```
69_Ga   : a_i =  60.11 %, m_i =   68.92558
71_Ga   : a_i =  39.89 %, m_i =   70.92471
```

We want to examine the effect of isotope composition on <b><i>&kappa;</i></b><sub>latt</sub>.
The required mass and variance parameters can be prepared using `phono3py-isotopes` using the `--site-average` option and entering the two isotopic masses in place of atomic symbols in the atoms list:

```
$ phono3py-isotopes 68.92558 70.92471, As --site-average --site-occupation="0.5 0.5, 1.0"
```

This performs a calculation with a 50/50 mix of two (arbitrary) atoms with masses of 68.92558 and 70.92471 amu at the Ga site:

```
Site 1 (?, ?)
-------------

  ?       : a_i =  50.00 %, m_i =   68.92558
  ?       : a_i =  50.00 %, m_i =   70.92471

  m_ave = 69.92515
  m_var = 2.04341e-04
```

The occupation fractions can be varied to simulate a range of isotopic compositions:

| % <sup>69</sup>Ga | % <sup>71</sup>Ga | Ave. Mass [amu] | Mass Var.   |
| ----------------- | ----------------- | --------------- | ----------- |
|               100 |                 0 |        68.92558 |           - |
|                90 |                10 |        69.12549 | 7.52745e-05 |
|                80 |                20 |        69.32541 | 1.33051e-04 |
|                70 |                30 |        69.52532 | 1.73626e-04 |
|                60 |                40 |        69.72523 | 1.97294e-04 |
|                50 |                50 |        69.92515 | 2.04341e-04 |
|                40 |                60 |        70.12506 | 1.95050e-04 |
|                30 |                70 |        70.32497 | 1.69700e-04 |
|                20 |                80 |        70.52488 | 1.28563e-04 |
|                10 |                90 |        70.72480 | 7.19087e-05 |
|                 0 |               100 |        70.92471 |           - |

At this point, a shell script is probably in order:

```bash
#!/bin/bash

function RunPhono3py() {
  phono3py --dim="2 2 2" --dim-fc2="3 3 3" --pa="0 1/2 1/2  1/2 0 1/2  1/2 1/2 0" \
    --fc2 --fc3 -v --br --mesh="32 32 32" \
    --mass="${1} 74.92160" --mass-variances="${2} 0.0" -o "${3}"
  }

RunPhono3py 68.92558 0           "iso.100-0"
RunPhono3py 69.12549 7.52745e-05 "iso.90-10"
RunPhono3py 69.32541 1.33051e-04 "iso.80-20"
RunPhono3py 69.52532 1.73626e-04 "iso.70-30"
RunPhono3py 69.72523 1.97294e-04 "iso.60-40"
RunPhono3py 69.92515 2.04341e-04 "iso.50-50"
RunPhono3py 70.12506 1.95050e-04 "iso.40-60"
RunPhono3py 70.32497 1.69700e-04 "iso.30-70"
RunPhono3py 70.52488 1.28563e-04 "iso.20-80"
RunPhono3py 70.72480 7.19087e-05 "iso.10-90"
RunPhono3py 70.92471 0           "iso.0-100"
```

Note again that we have not used the `--read-gamma` option because we are changing the average mass at each step.

<table>
  <tr>
    <th rowspan="2" style="vertical-align:bottom;">% <sup>69</sup>Ga</th>
    <th rowspan="2" style="vertical-align:bottom;">% <sup>79</sup>Ga</th>
    <th colspan="2"><i>&kappa;</i><sub>latt</sub> [W m<sup>-1</sup> K<sup>-1</sup>]</th>
  </tr>
 <tr>
    <th><i>T</i> = 100 K</th>
    <th><i>T</i> = 300 K</th>
  </tr>
  <tr><td>100</td><td>  0</td><td>159.5</td><td>38.03</td></tr>
  <tr><td> 90</td><td> 10</td><td>153.3</td><td>37.60</td></tr>
  <tr><td> 80</td><td> 20</td><td>149.0</td><td>37.28</td></tr>
  <tr><td> 70</td><td> 30</td><td>146.2</td><td>37.05</td></tr>
  <tr><td> 60</td><td> 40</td><td>144.6</td><td>36.90</td></tr>
  <tr><td> 50</td><td> 50</td><td>144.0</td><td>36.84</td></tr>
  <tr><td> 40</td><td> 60</td><td>144.3</td><td>36.84</td></tr>
  <tr><td> 30</td><td> 70</td><td>145.7</td><td>36.93</td></tr>
  <tr><td> 20</td><td> 80</td><td>148.3</td><td>37.10</td></tr>
  <tr><td> 10</td><td> 90</td><td>152.2</td><td>37.35</td></tr>
  <tr><td>  0</td><td>100</td><td>157.9</td><td>37.69</td></tr>
</table>

<img src="Resources/phono3py-isotopes_TutorialC.png" alt="phono3py-isotopes_TutorialC.png" width="750">


## Notes and References
----------

The equations in this document were produced using the [Online LaTeX Equation Editor](https://www.codecogs.com/latex/eqneditor.php) from [CodeCogs](https://www.codecogs.com/).

1. <a name="Ref1"></a> A. Togo, L. Chaput and I. Tanaka, *Physical Review B* **91**, 093206 (**2015**), DOI: [10.1103/PhysRevB.91.094306](https://doi.org/10.1103/PhysRevB.91.094306)
2. <a name="Ref2"></a> S.-I. Tamura, *Physical Review B* **27** (*2*), 858-866 (**1983**), DOI: [10.1103/PhysRevB.27.858](https://doi.org/10.1103/PhysRevB.27.858)
3. <a name="Ref3"></a> J. Carrete, B. Vermeersch, A. Katre, A. van Roekeghem, T. Wan, G. K. H. Madsen and N. Mingo, *Computer Physics Communications* **220**, 351-362 (**2017**), DOI: [10.1016/j.cpc.2017.06.023](https://doi.org/10.1016/j.cpc.2017.06.023)
