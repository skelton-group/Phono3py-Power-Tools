# PhonopyImporter/CASTEP.py


# ----------------
# Module Docstring
# ----------------

""" Contains routines for working with the CASTEP code. """


# -------
# Imports
# -------

import numpy as np


# ---------
# Functions
# ---------

def ReadPhonon(file_path):
    """
    Parse the CASTEP .phonon file at file_path.

    Return value:
        A (params, structure_data, q_point_data) tuple containing the data read in from the .phonon file.
            * params: { num_atoms : int, num_bands : int, num_qpts : int, 'freq_units' : string, 'ir_units' : string, 'raman_units' : string}
            * structure_data: (v_latt, atom_pos, atom_types, atom_mass)
            * q_point_data: [(q_pt, q_wt, freqs, ir_ints, eigenvectors)]
    """

    # Parameters to capture.

    params, structure_data, q_point_data = None, None, None

    # Read and parse input file.

    with open(file_path, 'r') as input_reader:
        # Read header.

        assert next(input_reader).strip() == "BEGIN header"

        # Read calculation parameters.

        params = { }

        capture = [
            ("Number of ions"       , 'num_atoms'  , int ),
            ("Number of branches"   , 'num_bands'  , int ),
            ("Number of wavevectors", 'num_qpts'   , int ),
            ("Frequencies in"       , 'freq_units' , None),
            ("IR intensities in"    , 'ir_units'   , None),
            ("Raman activities in"  , 'raman_units', None)
            ]

        for starts_with, params_key, conv_func in capture:
            line = next(input_reader).strip()

            assert line.startswith(starts_with)

            param = line.replace(starts_with, '').strip()

            if conv_func is not None:
                param = conv_func(param)

            params[params_key] = param

        assert next(input_reader).strip() == "Unit cell vectors (A)"

        # Read lattice vectors.

        v_latt = [
            [float(item) for item in next(input_reader).strip().split()[:3]]
                for i in range(0, 3)
            ]

        assert next(input_reader).strip() == "Fractional Co-ordinates"

        # Read atom data.

        atom_data = []

        for i in range(0, params['num_atoms']):
            elements = next(input_reader).strip().split()

            assert len(elements) >= 5 and int(elements[0]) == i + 1

            atom_pos = [float(item) for item in elements[1:4]]
            atom_type = str(elements[4])
            atom_mass = float(elements[5])

            atom_data.append(
                (atom_pos, atom_type, atom_mass)
                )

        assert next(input_reader).strip() == "END header"

        # Read frequencies/eigenvectors for each calculated wavevector.

        q_point_data = []

        for i in range(0, params['num_qpts']):
            # Read wavevector coordinates and weight.

            elements = next(input_reader).strip().split()

            assert len(elements) >= 6 and elements[0] == "q-pt=" and int(elements[1]) == i + 1

            q = [float(item) for item in elements[2:5]]
            w = float(elements[5])

            # Read frequencies and spectroscopic activities.

            freqs, ir_ints = [], []

            for j in range(0, params['num_bands']):
                elements = next(input_reader).strip().split()

                assert len(elements) >= 3 and int(elements[0]) == j + 1

                freqs.append(
                    float(elements[1])
                    )

                ir_ints.append(
                    float(elements[2])
                    )

            # Read eigenvectors.

            assert next(input_reader).strip() == "Phonon Eigenvectors"

            headers = next(input_reader).strip().split()

            expected_headers = ["Mode", "Ion", "X", "Y", "Z"]

            for j, expected_header in enumerate(expected_headers):
                assert headers[j] == expected_header

            eigenvectors = []

            for j in range(0, params['num_bands']):
                eigenvector = []

                for k in range(0, params['num_atoms']):
                    elements = next(input_reader).strip().split()

                    assert len(elements) >= 8 and int(elements[0]) == j + 1 and int(elements[1]) == k + 1

                    eigenvector.append(
                        [float(elements[i]) + 1.0j * float(elements[i + 1]) for i in range(2, 8, 2)]
                        )

                eigenvectors.append(eigenvector)

        q_point_data.append(
            (q, w, freqs, ir_ints, eigenvectors)
            )

        # Reformat data.

        v_latt = [np.array(v, dtype = np.float64) for v in v_latt]

        atom_pos = [
            np.array(pos, dtype = np.float64)
                for pos, _, _ in atom_data
            ]

        atom_types = [atom_type for _, atom_type, _ in atom_data]
        atom_mass = [atom_mass for _, _, atom_mass in atom_data]

        structure_data = (v_latt, atom_pos, atom_types, atom_mass)

        for i, (q, w, freqs, ir_ints, eigenvectors) in enumerate(q_point_data):
            q = np.array(q, dtype = np.float64)

            for j, eigenvector in enumerate(eigenvectors):
                eigenvectors[j] = np.array(eigenvector, dtype = np.complex128)

            q_point_data[i] = (q, w, freqs, ir_ints, eigenvectors)

    # Returm results

    return (params, structure_data, q_point_data)
