""" Bio-Logic OEM package python API.

This module provides helper functions to the ctypes module,
and can be imported as a whole when low level C interfacing is required.
"""

import binascii

from ctypes import (
    c_bool,
    c_byte,
    c_int8,
    c_uint8,
    c_int32,
    c_uint32,
    c_float,
    c_double,
    c_void_p,
    c_char_p,
    Structure,
    POINTER,
    sizeof,
    addressof,
    string_at,
    create_string_buffer,
    WinDLL,
)

#------------------------------------------------------------------------------#

# pointer version of types

c_float_p = POINTER(c_float)
c_int32_p = POINTER(c_int32)
c_uint32_p = POINTER(c_uint32)

# check on the size of pointers
c_is_64b = (sizeof(c_void_p) == 8)

#==============================================================================#

def c_dump (cobj) :
    """Print both byte version of object and hex dump."""
    l = sizeof(cobj)
    a = addressof(cobj)
    b = string_at(a,l)
    h = binascii.hexlify(b)
    print(b,'\n',h)

#------------------------------------------------------------------------------#

# helper class to be used when buffer+sizeof are needed

class c_buffer :

    def __init__ (self, size) :
        """Initialize a bytes buffer of given size, using a given encoding.

        The buffer goes along its length, which can be adjusted to the actual value during a call.
        """
        self._buf = create_string_buffer(size)
        self._len = c_uint32(len(self._buf))

    @property
    def parm (self) :
        """mimic ctypes style of embedding the parameter, which is a couple. """
        return self._buf, self._len

    @property
    def raw(self) :
        return self._buf

    def to_ascii (self) :
        """Extract the contents of the buffer using the actual length and turn it to a string."""
        buflen = min(len(self._buf), self._len.value)  # truncate if _len is invalid
        return (
            self._buf.raw[:buflen]
                .rstrip(b'\0')
                .decode('ascii', errors='backslashreplace')
        )

class utf16_buffer:
    def __init__ (self, size) :
        """Initialize a bytes buffer of given size, using a given encoding.

        The buffer goes along its length, which can be adjusted to the actual value during a call.
        """
        self._buf = create_string_buffer(size)
        self._size = c_uint32(len(self._buf)//4)  # number of characters, not byte length!

    @property
    def parm (self) :
        """mimic ctypes style of embedding the parameter, which is a couple. """
        return self._buf, self._size

    @property
    def raw(self) :
        return self._buf

    def decode (self) :
        """Extract the contents of the buffer using the actual length and turn it to a string."""
        buflen = min(len(self._buf), self._size.value * 4)
        s = (
            self._buf.raw[:buflen]
                .decode('utf16', errors='backslashreplace')
                .rstrip('\0')
        )
        return s[:self._size.value]

#------------------------------------------------------------------------------#

class POD (Structure) :

    """ctypes Structure with helper methods."""

    @property
    def keys (self) :
        """Reproduce a dict behaviour."""
        keys = ( t[0] for t in self._fields_ )
        return keys

    def __repr__ (self) :
        """Return class name and fields one at a line."""
        entries = str(self).split(', ')
        cls = type(self).__name__
        en_clair = f"{cls} :\n  " + '\n  '.join(entries)
        return en_clair

    def __str__ (self) :
        """Return key-value pairs separated by commas."""
        entries = list()
        for name in self.keys :
            entries.append(f"{name}={getattr(self,name)}")
        en_clair = ', '.join(entries)
        return en_clair

    def __getattr__ (self,name) :
        """Access Structure fields with nested attributes."""
        i = name.rfind('.')
        if i == -1 :
            # Structure should already have provided the first level attribute.
            raise AttributeError(f"{type(self)} has no '{name}' attribute")
        else :
            o = getattr(self,name[:i])
            v = getattr(o,name[i+1:])
        return v

    def subset (self, *fields) :
        """Create a dict from a selection of Structure fields."""
        subset = dict()
        if len(fields) == 0 :
            # no field means all fields
            fields = self.keys
        for name in fields :
            value = getattr(self,name)
            subset += {name:value}
        return subset

#==============================================================================#
