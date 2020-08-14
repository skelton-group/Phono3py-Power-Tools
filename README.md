# Phono3py-Power-Tools

Tools for Phono(3)py power users.


## Installation

### Requirements

The command-line scripts are written in Python and collectively require the following packages:

* [NumPy](https://numpy.org)
* [Matplotlib](https://matplotlib.org)
* [H5py](https://www.h5py.org)

If you do not use Python, we recommend installing [Anaconda](https://www.anaconda.com) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html).
The packages are installed by default with Anaconda, and can be added to Miniconda using the `conda` package manager:

```bash
$ conda install numpy matplotlib h5py
```

Some of the scripts also use the Phonopy Python API and require Phonopy to be installed.
This can also be installed using `conda` - instructions [here](https://phonopy.github.io/phonopy/install.html).


### Downloading and setting up

The easiest way to download Phono3py-Power-Tools is to clone the repository with `git`:

```bash
$ git clone https://github.com/skelton-group/Phono3py-Power-Tools
```

Once done, make the command-line scripts executable:

```bash
$ cd Phono3py-Power-Tools
$ chmod +x phonopy-* phono3py-*
```

To avoid prefixing the scripts with their full path, add the repository folder to your `$PATH` variable - e.g.:

```bash
$ export PATH=${PATH}:/mnt/d/Repositories/Phono3py-Power-Tools
```

If you wish to use the `Phono3pyTools` Python package, you will also need to add the folder to your `$PYTHONPATH`:

```bash
$ export PYTHONPATH=${PYTHONPATH}:/mnt/d/Repositories/Phono3py-Power-Tools
```

### Updating

You can update by performing a `git pull` from the Phono3py-Power-Tools folder:

```bash
$ git pull 
```

If you have imported the Python package, or run any of the command-line scripts that do so, this will likely have created some cache files and you will get a `git` error similar to the following:

```
error: Your local changes to the following files would be overwritten by merge:
        phono3py-mode-plot
Please, commit your changes or stash them before you can merge.
Aborting
```

Presuming you do not have source code changes to commit, you can work around this error by `git stash`ing the "changes", deleting the "stashed" changes, and then running a `git pull`:

```bash
$ git stash
$ git stash clear
$ git pull
```

After updating, you will probably need to update the script permissions again:

```bash
$ chmod +x phonopy-* phono3py-*
``` 


## Utilities for Phonopy

### phonopy-get-comm-pts

Command-line script to list the commensurate wavevectors (**q**-points) associated with a chosen supercell expansion.
Documentation and a usage example [here](./Docs/phonopy-get-comm-pts.md).

### phonopy-get-trans-mat

Command-line script to find the transformation matrix between a conventional and primitive cell such as the `BPOSCAR` and `PPOSCAR` obtained with `phonopy --symmetry`.
Documentation and a usage example [here](./Docs/phonopy-get-trans-mat.md).

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

### phono3py-mode-plot

Command-line script for visualising the data from Phono3py `kappa-m*.hdf5` files.
Documentation including a tutorial can be found [here](./Docs/phono3py-mode-plot.md).


## Contributions, bug reports and feature requests

We are happy to accept contributions.
To report bugs or request new features, please use the [Issue Tracker](https://github.com/skelton-group/Phono3py-Power-Tools/issues).
If you use the programs in this repository in your work, please let us know [jonathan.skelton[at]manchester.ac.uk](mailto:jonathan.skelton@manchester.ac.uk) - we will collect them and put up a list of outputs.
