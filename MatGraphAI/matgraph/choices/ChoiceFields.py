from graphutils.forms import RelationMultipleChoiceField
from dal import autocomplete

COMPONENT_TYPE_CHOICES = {'membrane': 'Membrane',
                          'ccm': 'CCM',
                          'mea': 'MEA',
                          'gdl': 'GDL',
                          'station': 'Station',
                          'catalystlayer': 'Catalyst Layer',
                          'bipolarplates': 'Bipolar Plates',
                          'gde': 'GDE'}

GRANULARITY_TYPE_CHOICEFIELD = {'nano': 'NanoStructure',
                                'micro': 'MicroStructure',
                                'macro': 'Macrostructure'}

MEASUREMENT_TYPE_CHOICEFIELD = {'synchrotron_tomo': 'Synchrotron Tomography',
                                'fib': 'FIB',
                                'tem': 'TEM',
                                'afm': 'AFM'}

MATERIAL_STRUCTURE_CHOICEFIELD = {'crystal': 'Crystal',
                                  'amorph': 'Amorphous',
                                  'ink': 'Ink',
                                  'polycrystal': 'Polycrystaline'}

MATERIAL_TYPE_CHOICEFIELD = {'metal': 'Metal',
                             'semiconductor': 'Semiconductor',
                             'polymer': 'Polymer',
                             'ceramic': 'Ceramic',
                             'nanomaterial': 'Nanomaterial',
                             'energymaterial': 'Energymaterial'}

MATERIAL_NANOSTRUCTURE_CHOICEFIELD = {'0d': '0-D',
                                      '1d': '1-D',
                                      '2d': '2-D',
                                      '3d': '3-D'}


MATERIAL_MICROSTRUCTURE_CHOICEFIELD = {}

MATERIAL_MACROSTRUCTURE_CHOICEFIELD = {}

MATERIAL_LABEL_CHOICEFIELD = {'nanocrystal': 'Nano Crystaline',
                              'ink' : 'Ink',
                              'catalystlayer' : 'Catalyst Layer',
                              'natural': 'Natural',
                              'manufactured': 'Manufactured'}

INSTITUTION_TYPE_CHOICEFIELD = {'Government' : 'Government',
                                'Education' : 'Education',
                                'Nonprofit' : 'Nonprofit',
                                'Other' : 'Other',
                                'Facility' : 'Facility',
                                'Company' : 'Company',
                                'Archive' : 'Archive',
                                'Healthcare': 'Healthcare'}


