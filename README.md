# Phono3py-Tools

An assortment of tools for working with Phono(3)py.


## Utilities for Phonopy

### Phonopy-Importer

Provides a means to post-process phonon calculations in unsupported codes with Phonopy, by reverse transforming frequencies and eigenvectors to force constants.
Currently supports CASTEP.
More complete documentation can be found in the [project subfolder](./Phonopy-Importer).


## Utilities for Phono3py

### phono3py-get-kappa

Command-line script for extracting thermal-conductivity tensors (<b><i>&kappa;</i></b><sub>latt</sub>) from the `kappa-m*.hdf5` files produced by Phono3py to plain-text comma-separated values (CSV) files.
More complete documentation can be found [here](./Docs/phono3py-get-kappa.md).

### phono3py-isotopes

Command-line script to generate input for modelling the effect of mass variance on <b><i>&kappa;</i></b><sub>latt</sub>.
Documentation including usage examples can be found [here](./Docs/phono3py-isotopes.md).
