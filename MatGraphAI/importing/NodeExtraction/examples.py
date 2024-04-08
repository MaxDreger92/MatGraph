MATTER_AGGREGATION_EXAMPLES = [
    {
        'input':
"""Context: Catalyst Fabrication

Attribute/ColumnIndex:

identifier/1, name/2, name/material2, name/3, ratio/8, ratio/9, ratio/10
Table:

id, Catalyst1, Catalyst2, Support, ratio 1, ratio 2, ratio 3
Sample Row:

CT-1001, Pt, C, Pd, 50, 30, 20""",
        'output': """[
  {
    "attributes": {
      "name": [
        [
          {"value": "Catalyst", "index": "inferred"}
        ]
      ],
      "identifier": [
        [
          {"value": "CT-1001", "index": 1}
        ]
      ],
      "ratio": []
    }
  },
  {
    "attributes": {

      "name": [
        [
          {"value": "Catalyst", "index": "inferred"}
        ],
        [
          {"value": "Pt", "index": 2}
        ]
      ],
      "ratio": [
        [
          {"value": "50", "index": 8}
        ]
      ]
    }
  },
  {
    "attributes": {
      "name": [
                  [
          {"value": "CarbonSupport", "index": "inferred"}
        ],
        [
          {"value": "C", "index": 3}
        ]
      ],
      "ratio": [
        [
          {"value": "30", "index": 9}
        ]
      ]
    }
  },
  {
    "attributes": {
      "name": [
                  [
          {"value": "Catalyst", "index": "inferred"}
        ],
        [
          {"value": "Pd", "index": 4}
        ]
      ],
      "ratio": [
        [
          {"value": "20", "index": 10}
        ]
      ]
    }
  }
]"""    },]

PARAMETER_AGGREGATION_EXAMPLES = [
    {
        'input':"""Context: Measurement of the density of a material

Attribute/ColumnIndex: value/5, error/6, value/7
Table: pressure (pA), error, T
Sample Row: 1.2, 0.1, 27""",
        'output': """[
  {
    "attributes": {
      "name": [
        [
          {"value": "pressure", "index": "inferred"}
        ]
      ],
      "value": [
        [
          {"value": "1.2", "index": 5}
        ]
      ],
      "error": [
        [
          {"value": "0.1", "index": 6}
        ]
      ],
      "unit": [
        [
          {"value": "pA", "index": "inferred"}
        ]
      ]
    }
  },
  {
    "attributes": {
      "name": [
        [
          {"value": "temperature", "index": "inferred"}
        ]
      ],
      "value": [
        [
          {"value": "27", "index": 7}
        ]
      ],
      "unit": [
        [
          {"value": "C", "index": "inferred"}
        ]
      ]
    }
  }
]"""    },]

MANUFACTURING_AGGREGATION_EXAMPLES = [
    {
        'input':"""Context: Fabrication of a battery electrode

Attribute/ColumnIndex: identifier/2, name/3, name/8
Table: id, process 1, process 2
Sample Row: AS-2001, mixing, spray_coating""",
        'output': """[
  {
    "attributes": {
      "name": [
        [
          {"value": "Mixing", "index": 3}
        ]
      ],
      "identifier": [
        [
          {"value": "AS-2001", "index": 2}
        ]
      ]
    }
  },
  {
    "attributes": {
      "name": [
        [
          {"value": "Spray Coating", "index": 8}
        ]
      ]
    }
  }
]"""
    },]

