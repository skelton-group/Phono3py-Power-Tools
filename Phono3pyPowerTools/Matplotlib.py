# Phono3pyPowerTools/Matplotlib.py


# ----------------
# Module Docstring
# ----------------

""" Routines for working with Matplotlib. """


# -------
# Imports
# -------

import math

import numpy as np
import matplotlib as mpl

from matplotlib.ticker import FuncFormatter


# -------------------
# Default Initialiser
# -------------------

def InitialiseMatplotlib():
    """ Set some basic Matplotlib rc parameters for publication-ready plotting. """

    font_size = 8
    line_width = 0.5

    # Fix for matplotlb.font_manager defaulting to bold variant of Times on some systems -- adapted from https://github.com/matplotlib/matplotlib/issues/5574.

    try:
        del mpl.font_manager.weight_dict['roman']
        mpl.font_manager._rebuild()
    except KeyError:
        pass

    # Fonts.

    mpl.rc('font', **{ 'family' : 'serif', 'size' : font_size, 'serif' : 'Times New Roman' })

    mpl.rc('mathtext', **{ 'fontset' : 'custom', 'rm' : 'Times New Roman', 'it' : 'Times New Roman:italic', 'bf' : 'Times New Roman:bold' })

    # Axes, lines and patches.

    mpl.rc('axes' , **{ 'linewidth' : line_width, 'labelsize'       : font_size  })
    mpl.rc('lines', **{ 'linewidth' : line_width, 'markeredgewidth' : line_width })
    mpl.rc('patch', **{ 'linewidth' : line_width                                 })

    # Tick parameters.

    tick_params = {
        'major.width' : line_width,
        'minor.width' : line_width,
        'direction' : 'in'
        }

    mpl.rc('xtick', **tick_params )
    mpl.rc('ytick', **tick_params )

    mpl.rc('xtick', **{ 'top'   : True })
    mpl.rc('ytick', **{ 'right' : True })


# -----------------
# Utility Functions
# -----------------

def HSBColourToRGB(h, s, b):
    """ Convert a colour specified in the HSB colour system to RGB. """

    h %= 360.0

    temp_c = s * b
    temp_min = b - temp_c

    temp_h_prime = h / 60.0
    temp_x = temp_c * (1.0 - math.fabs((temp_h_prime % 2.0) - 1.0))

    r, g, b = 0.0, 0.0, 0.0

    if temp_h_prime < 1.0:
        r = temp_c
        g = temp_x
        b = 0
    elif temp_h_prime < 2.0:
        r = temp_x
        g = temp_c
        b = 0
    elif temp_h_prime < 3.0:
        r = 0
        g = temp_c
        b = temp_x
    elif temp_h_prime < 4.0:
        r = 0
        g = temp_x
        b = temp_c
    elif temp_h_prime < 5.0:
        r = temp_x
        g = 0
        b = temp_c
    else:
        r = temp_c
        g = 0
        b = temp_x

    return (r + temp_min, g + temp_min, b + temp_min)

def GetDefaultAxisLimits(axis_min, axis_max, data, log_scale = False):
    """
    If axis_min and/or axis_max are None, set to default values based on the range of values in data.

    Keyword args:
      log_scale -- if True, set defaults for plotting on a log scale (default: False)
    """

    # Only do something if either or both of axis_min and axis_max are not already set.

    if axis_min is None or axis_max is None:
        if log_scale:
            # To get a sensible axis range on a logarithmic scale, it is useful to exclude (spurious) small values.
            # A reasonably effective ad hoc way to do this is to select the largest 99 % of the values and round the minimum/maximum values down/up to the nearest powers of 10.

            sorted_data = np.sort(data)
            sorted_data = sorted_data[len(sorted_data) // 100:]

            if axis_min is None:
                axis_min = math.pow(10, math.floor(math.log10(np.min(sorted_data))))

            if axis_max is None:
                axis_max = math.pow(10, math.ceil(math.log10(np.max(sorted_data))))

        else:
            # A sensible axis range on a linear scale can be obtained by rounding the minimum/maximum values down/up to "order of magnitude" values.

            div = math.pow(10, math.floor(math.log10(np.max(data))))

            if axis_min is None:
                axis_min = div * math.floor(np.min(data) / div)

            if axis_max is None:
                axis_max = div * math.ceil(np.max(data) / div)

    # Return (possibly updated) min/max values.

    return (axis_min, axis_max)


# --------------------
# Formatting Functions
# --------------------

def FormatToMinDP(val, max_dp):
    """ Format val as a string with the minimum number of required decimal places, up to a maximum of max_dp. """

    num_dp = 0

    while True:
        pow = -1 * num_dp

        if val % (10 ** pow) == 0.0 or num_dp == max_dp:
            break

        num_dp += 1

    return "{{0:.{0}f}}".format(num_dp).format(val)

def FormatToStandardForm(val):
    """ Format val as a string in standard form. """

    power = math.floor(
        math.log10(val)
        )

    val = val / (10 ** power)

    if val == 1.0:
        return r"10$^{{{0:.0f}}}$".format(power)
    else:
        return r"{0:.1f} $\times$ 10$^{{{1:.0f}}}$".format(val, power)

def GetFixedPointFormatter(num_dp):
    """ Return a FuncFormatter object to display float values to num_dp decimal places. """

    format_str = r"{{0:.{0}f}}".format(num_dp)

    return FuncFormatter(
        lambda val, pos : format_str.format(val)
        )

def GetLogFormatter():
    """ Return a FuncFormatter object to display integer values x as 10^x """

    return FuncFormatter(
        lambda val, pos : r"10$^{{{0:.0f}}}$".format(int(val))
        )
