""" Bio-Logic OEM package technique constants.

This module provides an enumeration of technique identifiers which DLL calls return.

"""

from enum import Enum

#=============================================================================#

class TECH_ID (Enum) :
  NONE            =   0 # None
  OCV             = 100 # Open Circuit Voltage (Rest)
  CA              = 101 # Chrono-amperometry
  CP              = 102 # Chrono-potentiometry
  CV              = 103 # Cyclic Voltammetry
  PEIS            = 104 # Potentio Electrochemical Impedance Spectroscopy
  POTPULSE        = 105 # (unused)
  GALPULSE        = 106 # (unused)
  GEIS            = 107 # Galvano Electrochemical Impedance Spectroscopy
  STACKPEIS_SLAVE = 108 # Potentio Electrochemical Impedance Spectroscopy on stack
  STACKPEIS       = 109 # Potentio Electrochemical Impedance Spectroscopy on stack
  CPOWER          = 110 # Constant Power
  CLOAD           = 111 # Constant Load
  FCT             = 112 # (unused)
  SPEIS           = 113 # Staircase Potentio Electrochemical Impedance Spectroscopy
  SGEIS           = 114 # Staircase Galvano Electrochemical Impedance Spectroscopy
  STACKPDYN       = 115 # Potentio dynamic on stack
  STACKPDYN_SLAVE = 116 # Potentio dynamic on stack
  STACKGDYN       = 117 # Galvano dynamic on stack
  STACKGEIS_SLAVE = 118 # Galvano Electrochemical Impedance Spectroscopy on stack
  STACKGEIS       = 119 # Galvano Electrochemical Impedance Spectroscopy on stack
  STACKGDYN_SLAVE = 120 # Galvano dynamic on stack
  CPO             = 121 # (unused)
  CGA             = 122 # (unused)
  COKINE          = 123 # (unused)
  PDYN            = 124 # Potentio dynamic
  GDYN            = 125 # Galvano dynamic
  CVA             = 126 # Cyclic Voltammetry Advanced
  DPV             = 127 # Differential Pulse Voltammetry
  SWV             = 128 # Square Wave Voltammetry
  NPV             = 129 # Normal Pulse Voltammetry
  RNPV            = 130 # Reverse Normal Pulse Voltammetry
  DNPV            = 131 # Differential Normal Pulse Voltammetry
  DPA             = 132 # Differential Pulse Amperometry
  EVT             = 133 # Ecorr vs. time
  LP              = 134 # Linear Polarization
  GC              = 135 # Generalized corrosion
  CPP             = 136 # Cyclic Potentiodynamic Polarization
  PDP             = 137 # Potentiodynamic Pitting
  PSP             = 138 # Potentiostatic Pitting
  ZRA             = 139 # Zero Resistance Ammeter
  MIR             = 140 # Manual IR
  PZIR            = 141 # IR Determination with Potentiostatic Impedance
  GZIR            = 142 # IR Determination with Galvanostatic Impedance
  LOOP            = 150 # Loop (used for linked techniques)
  TO              = 151 # Trigger Out
  TI              = 152 # Trigger In
  TOS             = 153 # Trigger Set
  CPLIMIT         = 155 # Chrono-potentiometry with limits
  GDYNLIMIT       = 156 # Galvano dynamic with limits
  CALIMIT         = 157 # Chrono-amperometry with limits
  PDYNLIMIT       = 158 # Potentio dynamic with limits
  LASV            = 159 # Large amplitude sinusoidal voltammetry
  MP              = 167 # Modular Pulse
  CASG            = 169 # Constant amplitude sinusoidal micro galvano polarization
  CASP            = 170 # Constant amplitude sinusoidal micro potentio polarization

#=============================================================================#
