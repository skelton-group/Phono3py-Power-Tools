# Phono3pyPowerTools/Utilities.py


# ----------------
# Module Docstring
# ----------------

""" Miscellaneous utility functions. """


# -------
# Imports
# -------

import sys


# ---------
# CSV Files
# ---------

def OpenForCSVWriter(file_path):
    """ Open file_path for use with the csv.writer class and return a file object. """
    
    # This function works around a quirk (?) in the csv module.
    
    # On Windows, a csv.writer built around a file object created using open(file_path, 'w') inserts additional blank rows.
    # To work around this in Python 2.x the file needs to be opened in binary ('wb') mode.
    # To work around this in Python 3.x the file needs to be opened with the newline argument set to ''.
    
    if sys.version_info.major >= 3:
        return open(file_path, 'w', newline = '')
    else:
        return open(file_path, 'wb')
