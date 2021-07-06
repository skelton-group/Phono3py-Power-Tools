# Phono3pyPowerTools/Phono3pyIO.py


# ----------------
# Module Docstring
# ----------------

""" Routines for working with Phono3py files. """


# -------
# Imports
# -------

import math

import h5py

import numpy as np

import warnings


# ---------
# Constants
# ---------

ZeroTolerance = 1.0e-5


# -----------------
# FORCES_FC3 Parser
# -----------------

def IsForcesFC3(file_path):
    """ Peeks at file_path and returns True if it appears to be a Phono3py FORCES_FC3 file. """
    
    with open(file_path, 'r') as input_reader:
        return next(input_reader).strip() == "# File: 1"

def ReadForcesFC3(file_path):
    """
    Reads sets of forces from a Phono3py FORCES_FC3 file.
    
    Returns:
        A list of (disps, force_set) tuples.
        disps are lists of one or more (atom_index, disp) tuples listing the atomic displacements in the configuration.
        force_set is a list of vectors listing the forces on the atoms.
    """
    
    force_sets = []
    
    with open(file_path, 'r') as input_reader:
        # Temporary variables.
        
        disps, force_set = None, None
        
        for line in input_reader:
            line = line.strip()
            
            if line == "":
                break
            
            if line.startswith("# File:"):
                # Start of force set.
                
                # If the disps and force_set variables are not None, capture them.
                # The file number indicated in the first line should be incremental -> use as a sanity check.
                
                if disps is not None and force_set is not None:
                    force_sets.append(
                        (disps, force_set)
                        )
                    
                    disps, force_set = None, None
                
                file_number = int(line.replace("# File: ", ""))
                
                # Sanity check.
                                               
                assert file_number == len(force_sets) + 1
                
            elif line.startswith('#'):
                # Line gives the index of the displaced atom and the displacement direction.
                
                atom_index, disp_x, disp_y, disp_z = line[1:].strip().split()
                
                if disps is None:
                    disps = []
                
                disps.append(
                    (int(atom_index), np.array([float(disp_x), float(disp_y), float(disp_z)], dtype = np.float64))
                    )
            
            else:
                # Line gives the x, y and x components of the force on the atoms.
                
                f_x, f_y, f_z = line.strip().split()
                
                if force_set is None:
                    force_set = []
                
                force_set.append(
                    np.array([float(f_x), float(f_y), float(f_z)], dtype = np.float64)
                    )
        
        # Capture last read set if required.
        
        if disps is not None and force_set is not None:
            force_sets.append(
                (disps, force_set)
                )
        
    # Sanity checks.
    
    assert len(force_sets) > 0
    
    _, force_set = force_sets[0]
    
    num_atoms_sc = len(force_set)
    
    for _, force_set in force_sets[1:]:
        assert len(force_set) == num_atoms_sc
    
    # Return captured data.
    
    return force_sets


# -----------------------
# Phono3pyKappaHDF5 Class
# -----------------------

class Phono3pyKappaHDF5(object):
    """ Encapsulates a Phono3py kappa-m*.hdf5 file and provides an interface to extract data. """

    # -----------
    # Constructor
    # -----------

    def __init__(self, path_or_dataset):
        """ Initialise a Phono3pyKappaHDF5 object with an open h5py Dataset object or a file path. """

        if isinstance(path_or_dataset, h5py.Dataset):
            self._file_path = None
            self._kappa_hdf5 = path_or_dataset
        else:
            self._file_path = path_or_dataset
            self._kappa_hdf5 = None

    # ---------------
    # Private Methods
    # ---------------

    def _GetDataset(self):
        """
        Return the encapsulated h5py Dataset object.
        If the instance was initialised with a file path, this opens the file for reading.
        """

        if self._kappa_hdf5 is None:
            self._kappa_hdf5 = h5py.File(
                self._file_path, 'r'
                )

        return self._kappa_hdf5

    def _GetTIndex(self, temp):
        """ Retrieve the index of temp in the 'temperature' array. """

        t_index = np.argwhere(
            self.GetTemperature() == temp
            )

        if len(t_index) == 0:
            raise Exception("Error: temp = {0} K not found in 'temperature' array.".format(temp))

        (t_index, ), = t_index

        return t_index

    # ----------
    # Properties
    # ----------

    @property
    def NumBands(self):
        """ Returns the number of phonon bands per q-point. """

        _, nbnds = self.GetModeFreqs().shape

        return nbnds

    @property
    def NumQPts(self):
        """ Returns the number of unique q-points in the sampling mesh. """

        return len(self.GetQPointWeights())

    @property
    def IsLBTE(self):
        """ Returns True if the encapsuated dataset is an LBTE calculation. """

        return 'kappa_RTA' in self._GetDataset().keys()

    # ------------
    # Get* Methods
    # ------------

    def GetTemperature(self):
        """ Retrieve temperatures (shape: n_tmps) """

        return self._GetDataset()['temperature'][:]

    def GetKappa(self, lbte_rta = False):
        """
        Retrieve kappa (shape: n_tmps, 6)

        Keyword args:
          lbte_rta -- if the dataset is an LBTE calculation, return the RTA data (default: False)
        """

        if self.IsLBTE and lbte_rta:
            return self._GetDataset()['kappa_RTA'][:]
        else:
            return self._GetDataset()['kappa'][:]

    def GetKappaXX(self, lbte_rta = False):
        """
        Retrieve k_xx (shape: n_tmps).

        Keyword args:
          lbte_rta -- if the dataset is an LBTE calculation, return the RTA data (default: False)
        """

        return self.GetKappa(lbte_rta = lbte_rta)[:, 0]

    def GetKappaYY(self, lbte_rta = False):
        """
        Retrieve k_yy (shape: n_tmps).

        Keyword args:
          lbte_rta -- if the dataset is an LBTE calculation, return the RTA data (default: False)
        """

        return self.GetKappa(lbte_rta = lbte_rta)[:, 1]

    def GetKappaZZ(self, lbte_rta = False):
        """
        Retrieve k_zz (shape: n_tmps).

        Keyword args:
          lbte_rta -- if the dataset is an LBTE calculation, return the RTA data (default: False)
        """

        return self.GetKappa(lbte_rta = lbte_rta)[:, 2]

    def GetKappaAve(self, lbte_rta = False):
        """
        Retrieve k_ave = (k_xx + k_yy + k_zz) / 3 (shape: n_tmps).

        Keyword args:
          lbte_rta -- if the dataset is an LBTE calculation, return the RTA data (default: False)
        """

        return np.mean(
            self.GetKappa(lbte_rta = lbte_rta)[:, :3], axis = -1
            )

    def GetQPointWeights(self):
        """ Retrieve q-point weights (shape: n_qpts). """

        return self._GetDataset()['weight'][:]

    def GetModeFreqs(self):
        """ Retrieve mode frequencies (shape: n_qpts, n_bnds). """

        return self._GetDataset()['frequency'][:, :]

    def GetModeKappaAve(self, temp, lbte_rta = False):
        """
        Retrieve mode k_ave = (k_xx + k_yy + k_zz) / 3 at T = temp (shape: n_qpts, n_bnds).
        The k_ave is divided by the number of grid points N such that sum(mode_kappa_ave) == k_ave.

        Keyword args:
          lbte_rta -- if the dataset is an LBTE calculation, return the RTA data (default: False)
        """

        mode_kappa = None

        if self.IsLBTE and lbte_rta:
            mode_kappa = self._GetDataset()['mode_kappa_RTA']
        else:
            mode_kappa = self._GetDataset()['mode_kappa']

        t_index = self._GetTIndex(temp)

        mode_kappa_ave = np.mean(
            mode_kappa[t_index, :, :, :3], axis = -1
            )

        kappa_ref = self.GetKappaAve(lbte_rta = lbte_rta)[t_index]

        if math.fabs(mode_kappa_ave.sum() - kappa_ref) > ZeroTolerance:
            # Newer version of Phono3py -> divide by the the number of grid points.

            mode_kappa_ave_norm = mode_kappa_ave / self.GetQPointWeights().sum()

            if math.fabs(mode_kappa_ave_norm.sum() - kappa_ref) < ZeroTolerance:
                mode_kappa_ave = mode_kappa_ave_norm
            else:
                # A "fail safe" just in case.

                warnings.warn(
                    r"Failed to normalise modal k_ave - values will be returned as read from the file.", RuntimeWarning
                    )

        return mode_kappa_ave

    def GetModeCV(self, temp):
        """ Retrieve mode C_V at T = temp (shape: n_qpts, n_bnds). """

        t_index = self._GetTIndex(temp)

        return self._GetDataset()['heat_capacity'][t_index, :, :]

    def GetModeGVNorm(self):
        """ Retrieve mode group velocity norms |v__g| (units: m/s, shape: n_qpts, n_bnds). """

        return 1.0e2 * np.linalg.norm(
            self._GetDataset()['group_velocity'][:, :, :], axis = -1
            )

    def GetModeGamma(self, temp):
        """ Retrieve mode linewidths Gamma at T = temp (shape: n_qpts, n_bnds). """

        t_index = self._GetTIndex(temp)

        return self._GetDataset()['gamma'][t_index, :, :]

    def GetModeTau(self, temp):
        """ Retrieve mode lifetimes at T = temp (units: ps, shape: n_qpts, n_bnds). """

        mode_gamma = self.GetModeGamma(temp)

        return np.where(
            mode_gamma > 0.0, 1.0 / (2.0 * 2.0 * math.pi * mode_gamma), 0.0
            )

    def GetModeMFPNorm(self, temp):
        """ Retrieve mode mean free paths |\Lambda| at T = temp (units: nm, shape: n_qpts, n_bnds). """

        return 1.0e-3 * self.GetModeGVNorm() * self.GetModeTau(temp)

    def GetModePQJ(self):
        """ Retrieve averaged phonon-phonon interaction strengths P_qj. """

        return self._GetDataset()['ave_pp'][:, :]

    # -------------------
    # Convenience Methods
    # -------------------

    def GetCumulativeKappaAve(self, temp, lbte_rta = False):
        """
        Return a (freq, kappa_cum) tuple with the cumulative k_ave as a function of frequency.

        Keyword args:
          lbte_rta -- if the dataset is an LBTE calculation, return the RTA data (default: False)
        """

        mode_freqs = self.GetModeFreqs()

        mode_kappa = self.GetModeKappaAve(
            temp, lbte_rta = lbte_rta
            )

        temp = sorted(
            [(f, k) for f, k in zip(mode_freqs.ravel(), mode_kappa.ravel())]
            )

        temp = np.array(
            temp, dtype = np.float64
            )

        freqs, kappa = temp.T

        kappa_cum = np.cumsum(kappa)

        return (freqs, kappa_cum)

    # ---------------
    # Utility Methods
    # ---------------

    def Close(self):
        """
        Close the internal h5py Dataset object, if opened by this instance.
        (If the instance was initialised with an open Dataset object, this method does nothing.)
        Once Close() has been called, further property reads and class methods are likely to fail.
        """

        if self._file_path is not None and self._kappa_hdf5 is not None:
            self._kappa_hdf5.close()

    # ---------------
    # "Magic" methods
    # ---------------

    def __enter__(self):
        """ Implementation of the __enter__() method for use in with statements. """

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """ Implementation of the __exit__() method for use in with statements. """

        self.Close()
