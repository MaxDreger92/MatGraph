""" Bio-Logic OEM package python API.

This module provides simple functions that are general purpose,
and prone to be used in several modules.
"""

import os
import logging

_log = logging.getLogger(__name__)

#------------------------------------------------------------------------------#

def warn_diff (msg,cmp) :
    """Check a predicate (assert) or a mismatch, and on error print a message."""
    if type(cmp) is bool :
        not_ok = not cmp
        if not_ok :
            _log.warning(f"{msg} failed")
    else :
        not_ok = (cmp[0] != cmp[1])
        if not_ok :
            _log.warning(f"{msg} {cmp}")
    return not_ok

#------------------------------------------------------------------------------#

def error_diff (msg,cmp) :
    """Check a predicate (assert) or a mismatch, and on error raise an exception."""
    if type(cmp) is bool :
        if not cmp :
            raise RuntimeError(f"{msg}")
    else :
        if (cmp[0] != cmp[1]) :
            raise RuntimeError(f"{msg} {cmp}")

#------------------------------------------------------------------------------#

def prepend_path (path, filename) :
    """Prepend a path to filename in case one is not already provided."""
    if path :
        segs = os.path.split(filename)
        if (segs[0] == '') and (filename != '') :
            filename = path + filename
    return filename

#------------------------------------------------------------------------------#

def file_complete (filename, an_ext) :
    """Append an extension to a filename unless the file already exists or if it already has one."""
    if not os.path.isfile(filename) :
        root,ext = os.path.splitext(filename)
    if not ext :
            filename = root + an_ext
    return filename

#------------------------------------------------------------------------------#

def pp_plural (nb, label, num=True, nothing='') :
    """Return a user friendly version of an ordinal and a label.
    
       num is used to force a number version,
       nothing is what to say if there is nothing
    """
    if nb == 0 :
        if nothing :
            en_clair = f"{nothing}"
        else :
            en_clair = f"{0 if num else 'no'} {label}"
    elif nb == 1 :
        en_clair = f"{1 if num else 'one'} {label}"
    else :
        en_clair = f"{nb} {label}s"
    return en_clair

#==============================================================================#
