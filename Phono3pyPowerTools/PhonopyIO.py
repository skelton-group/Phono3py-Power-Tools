# Phono3pyPowerTools/PhonopyIO.py


# ----------------
# Module Docstring
# ----------------

""" Routines for working with Phonopy files. """


# -------
# Imports
# -------

import numpy as np


# -----------------
# FORCE_SETS Parser
# -----------------


def IsForceSets(file_path):
    """ Peeks at file_path and returns True if it appears to be a Phonopy FORCE_SETS file. """
    
    with open(file_path, 'r') as input_reader:
        line_1 = next(input_reader).strip()
        line_2 = next(input_reader).strip()
        line_3 = next(input_reader).strip()
        
        return line_1.isdigit() and line_2.isdigit() and line_3 == ""

def ReadForceSets(file_path):
    """
    Reads sets of forces from a Phonopy FORCE_SETS file.
    
    Returns:
        A list of (disps, force_set) tuples.
        disps are lists of one or more (atom_index, disp) tuples listing the atomic displacements in the configuration.
        force_set is a list of vectors listing the forces on the atoms.
    """
    
    force_sets = []
    
    with open(file_path, 'r') as input_reader:
        # Read number of atoms in supercell.
        
        num_atoms_sc = int(
            next(input_reader).strip()
            )
        
        # Read number of configurations.
        
        num_configs = int(
            next(input_reader).strip()
            )
        
        for _ in range(num_configs):
            # Skip blank line.
            
            next(input_reader)

            # Atom index.
            
            atom_index = int(
                next(input_reader).strip()
                )
            
            # Displacement.
            
            disp_x, disp_y, disp_z = next(input_reader).strip().split()
            
            atom_disp = np.array(
                [float(disp_x), float(disp_y), float(disp_z)], dtype = np.float64
                )
            
            # Forces.
            
            force_set = []
            
            for _ in range(num_atoms_sc):
                f_x, f_y, f_z = next(input_reader).strip().split()
                
                force_set.append(
                    np.array([float(f_x), float(f_y), float(f_z)], dtype = np.float64)
                    )
            
            # Capture data.
            
            force_sets.append(
                ((atom_index, atom_disp), force_set)
                )
    
    # Sanity checks.
        
    assert len(force_sets) > 0
    
    _, force_set = force_sets[0]
    
    num_atoms_sc = len(force_set)
    
    for _, force_set in force_sets[1:]:
        assert len(force_set) == num_atoms_sc
    
    # Return captured data.
    
    return force_sets
