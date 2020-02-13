# Common.py


# ----------------
# Module Docstring
# ----------------

""" Core functions for preparing Phonopy input files using the default VASP formats. """


# -------
# Imports
# -------

import math
import os
import warnings

import numpy as np

from phonopy import Phonopy
from phonopy.structure.atoms import PhonopyAtoms
from phonopy.file_IO import write_FORCE_CONSTANTS
from phonopy.harmonic.dynmat_to_fc import DynmatToForceConstants
from phonopy.units import VaspToTHz, VaspToCm


# ---------
# Constants
# ---------

""" Tolerance for comparing positions. """

_SymPrec = 1.0e-5


# ---------
# Functions
# ---------

def _CheckStructure(lattice_vectors, atom_types, atom_pos, atom_mass = None):
    """ Implements checks on structure input data common to both the WritePOSCAR() and BuildForceConstants() routines. """

    # Check required variables are not None.

    for param in lattice_vectors, atom_types, atom_pos:
        assert param is not None

    # Check shape of lattice vectors.

    dim_1, dim_2 = np.shape(lattice_vectors)

    assert dim_1 == dim_2 == 3

    # Check at least one atom has been supplied.

    assert len(atom_types) > 0

    # Check the shape of atom_pos.

    dim_1, dim_2 = np.shape(atom_pos)

    assert dim_1 == len(atom_types) and dim_2 == 3

    # The functions in this module assume atom positions are in fractional coordinates.
    # Check that the absolute positions are all in the range [0, 1] and, if not, issue a warning.

    if (np.abs(atom_pos) > 1.0).any():
        warnings.warn("Functions in the Common module assume atom positions are in fractional coordinates.", RuntimeWarning)

    # If supplied, check the length of atom_mass.

    if atom_mass is not None:
        assert len(atom_mass) == len(atom_types)

def WritePOSCAR(lattice_vectors, atom_types, atom_pos, file_path = r"POSCAR.vasp", structure_name = None):
    """
    Write a structure to a VASP POSCAR file.

    Args:
        lattice_vectors -- 3x3 matrix containing the lattice vectors
        atom_types -- list of atomic symbols
        atom_pos -- list of atomic positions ** in fractional coordinates **
        file_path -- path to output file to write (default: POSCAR.vasp)
        structure_name -- name of structure for output file (default: derived from file_path)
    """

    # Check input.

    _CheckStructure(lattice_vectors, atom_types, atom_pos)

    # If structure_name is not supplied, obtain one from the file path.

    _, tail = os.path.split(file_path)
    root, _ = os.path.splitext(tail)

    structure_name = root

    # The POSCAR format requires a set of atom types and counts.

    atom_types_counts = []

    type_temp, count_temp = atom_types[0], 1

    for atom_type in atom_types[1:]:
        if atom_type == type_temp:
            count_temp += 1
        else:
            atom_types_counts.append(
                (type_temp, count_temp)
                )

            type_temp, count_temp = atom_type, 1

    atom_types_counts.append(
        (type_temp, count_temp)
        )

    # Write output file.

    with open(r"POSCAR.vasp", 'w') as output_writer:
        # Title line.

        output_writer.write(
            "{0}\n".format(structure_name)
            )

        # Scale factor.

        output_writer.write(
            "  {0: >19.16f}\n".format(1.0)
            )

        # Lattice vectors.

        for ax, ay, az in lattice_vectors:
            output_writer.write(
                "  {0: >21.16f}  {1: >21.16f}  {2: >21.16f}\n".format(ax, ay, az)
                )

        # Atom types and counts.

        for atom_type, _ in atom_types_counts:
            output_writer.write(
                "  {0: >3}".format(atom_type)
                )

        output_writer.write("\n")

        for _, atom_count in atom_types_counts:
            output_writer.write(
                "  {0: >3}".format(atom_count)
                )

        output_writer.write("\n")

        # Atom positions.

        output_writer.write("Direct\n")

        for x, y, z in atom_pos:
            output_writer.write(
                "  {0: >21.16f}  {1: >21.16f}  {2: >21.16f}\n".format(x, y, z)
                )

def BuildForceConstants(lattice_vectors, atom_types, atom_pos, q_pts, freqs, eigs, sc_dim, freq_units = 'thz', atom_mass = None, file_path = r"FORCE_CONSTANTS"):
    """
    Use the Phonopy API to take a set of frequencies and eigenvectors, construct a dynamical matrix, transform to a set of force constants, and write out a Phonopy FORCE_CONSTANTS file.

    Args:
        lattice_vectors -- 3x3 matrix containing the lattice vectors
        atom_types -- list of atomic symbols
        atom_pos -- list of atomic positions ** in fractional coordinates **
        q_pts -- list of q-point coordinates
        freqs -- n_q sets of Frequencies
        eigs -- n_q sets of eigenvectors
        sc_dim -- (equivalent) supercell dimension for preparing force constants
        freq_units -- units of freqs ('thz' or 'inv_cm' -- default: 'thz')
        atom_mass -- (optional) list of atomic masses (default: taken from Phonopy internal database)
        file_path -- path to FORCE_CONSTANTS file to write (default: FORCE_CONSTANTS)
    """

    # Check input.

    _CheckStructure(lattice_vectors, atom_types, atom_pos, atom_mass)

    for param in q_pts, freqs, eigs, sc_dim:
        assert param is not None

    dim_1, dim_2 = np.shape(q_pts)

    assert dim_1 > 0 and dim_2 == 3

    n_at = len(atom_types)

    n_q = dim_1
    n_b = 3 * n_at

    dim_1, dim_2 = np.shape(freqs)

    assert dim_1 == n_q and dim_2 == n_b

    dim_1, dim_2, dim_3, dim_4 = np.shape(eigs)

    assert dim_1 == n_q and dim_2 == n_b and dim_3 == n_at and dim_4 == 3

    dim_1, = np.shape(sc_dim)

    assert dim_1 == 3

    # Obtain a frequency conversion factor to "VASP units".

    freq_conv_factor = None

    if freq_units == 'thz':
        freq_conv_factor = VaspToTHz
    elif freq_units == 'inv_cm':
        freq_conv_factor = VaspToCm

    if freq_conv_factor is None:
        raise Exception("Error: Unknown freq_units '{0}'.".format(freq_units))

    # Create a Phonopy-format structure.

    structure = PhonopyAtoms(
        symbols = atom_types, masses = atom_mass, scaled_positions = atom_pos, cell = lattice_vectors
        )

    # Convert supercell expansion to a supercell matrix.

    dim_1, dim_2, dim_3 = sc_dim

    if dim_1 != dim_2 != dim_2 != 1:
        warnings.warn("The dynamical matrix -> force constants transform has only been tested at the Gamma point; please report issues to the developer.", RuntimeWarning)

    sc_matrix = [[dim_1, 0, 0], [0, dim_2, 0], [0, 0, dim_3]]

    # Use the main Phonopy object to obtain the primitive cell and supercell.

    calculator = Phonopy(structure, sc_matrix)

    primitive = calculator.get_primitive();
    supercell = calculator.get_supercell();

    # Use the DynmatToForceConstants object to convert frequencies/eigenvectors -> dynamical matrices -> force constants.

    dynmat_to_fc = DynmatToForceConstants(primitive, supercell)

    commensurate_points = dynmat_to_fc.get_commensurate_points()

    # If an input code does not use crystal symmetry or outputs data at all q-points in a sampling mesh, data may be provided for more q-points than there are commensurate points.
    # However, for most codes this would be an odd situation -> issue a warning.

    if len(commensurate_points) != n_q:
        warnings.warn("The number of entries in the q_pts list does not equal the number of commensurate points expected for the supplied supercell matrix.", RuntimeWarning)

    # Map commensurate points in Phonopy setup to q-points in input data.

    map_indices = []

    for qx_1, qy_1, qz_1 in commensurate_points:
        map_index = None

        for i, (qx_2, qy_2, qz_2) in enumerate(q_pts):
            if math.fabs(qx_2 - qx_1) < _SymPrec and math.fabs(qy_2 - qy_1) < _SymPrec and math.fabs(qz_2 - qz_1) < _SymPrec:
                map_index = i
                break

        if map_index is None:
            raise Exception("Error: Expected q = ({0: >6.3f}, {1: >6.3f}, {2: >6.3f}) in the q_pts list (this may be a bug; please report to the developer).".format(qx_1, qy_1, qz_1))

        # Sanity check.

        assert map_index not in map_indices

        map_indices.append(map_index)

    # Arrange the frequencies and eigenvectors to the layout required by Phonopy.

    freq_sets, eig_sets = [], []

    for index in map_indices:
        freq_sets.append(
            [freq / freq_conv_factor for freq in freqs[index]]
            )

        eig = eigs[index]

        # Eigenvectors need to be a 3Nx3N matrix in the format:
        # 1_x -> [ m_1, ..., m_3N ]
        # 1_y -> [ m_1, ..., m_3N ]
        # ...
        # N_z -> [ m_1, ..., m_3N ]

        eig_rows = []

        for i in range(0, n_at):
            for j in range(0, 3):
                eig_row = []

                for k in range(0, n_b):
                    eig_row.append(eig[k][i][j])

                eig_rows.append(eig_row)

        eig_sets.append(eig_rows)

    freq_sets = np.array(freq_sets, dtype = np.float64)
    eig_sets = np.array(eig_sets, dtype = np.complex128)

    # Use the DynmatToForceConstants object to build the dynamical matrices, reverse transform to the force constants, and write a Phonopy FORCE_CONSTANTS file.

    dynmat_to_fc.set_dynamical_matrices(freq_sets, eig_sets)

    dynmat_to_fc.run()

    write_FORCE_CONSTANTS(
        dynmat_to_fc.get_force_constants(), filename = file_path
        )
