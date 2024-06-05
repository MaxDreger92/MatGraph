MATTER_AGGREGATION_EXAMPLES = [
    {
        'input':
"""Context: 
    Domain: Catalyst Fabrication
    Table: 
        headers: id, Catalyst1, Catalyst2, I/C, Support, milltime, temp, ratio 1, ratio 2, ratio 3
        first_row: CT-1001, Pt, Pd, 0.8, C, 60, 28, 50, 30, 20
Input Data:
[
    {"ColumnIndex": 1, "AttributeType": "identifier", "TableHeader": "id", "SampleRow": "CT-1001"},
    {"ColumnIndex": 2, "AttributeType": "name", "TableHeader": "Catalyst1", "SampleRow": "Pt"},
    {"ColumnIndex": 4, "AttributeType": "name", "TableHeader": "Catalyst2", "SampleRow": "Pd"},
    {"ColumnIndex": 5, "AttributeType": "name", "TableHeader": "Support", "SampleRow": "C"},
    {"ColumnIndex": 8, "AttributeType": "ratio", "TableHeader": "ratio 1", "SampleRow": 50},
    {"ColumnIndex": 9, "AttributeType": "ratio", "TableHeader": "ratio 2", "SampleRow": 30},
    {"ColumnIndex": 10, "AttributeType": "ratio", "TableHeader": "ratio 3", "SampleRow": 20}
]""",
        'output': """[
  {
    "attributes": {
      "name": [
          {"value": "Catalyst", "reference": "header"}        
          ],
      "identifier": [
        [
          {"value": "CT-1001", "reference": 1}
        ]
      ]
    }
  },
  {
    "attributes": {

      "name": [
          {"value": "Catalyst", "reference": "header"},
          {"value": "Pt", "reference": 2}
      ]
    }
  },
  {
    "attributes": {
      "name": [
          {"value": "CarbonSupport", "reference": "header"},
          {"value": "C", "reference": 4}
      ]
    }
  },
  {
    "attributes": {
      "name": [
          {"value": "Catalyst", "reference": "header"},
          {"value": "Pd", "reference": 5}
      ]
    }
  }
]"""    },]

PARAMETER_AGGREGATION_EXAMPLES = [
    {
        'input':"""Context: Measurement of the density of a material

Attribute/ColumnIndex: 
value/5, error/6, value/7

Table: 
pressure (pA), error, T

Sample Row: 
1.2, 0.1, 27""",
        'output': """[
  {
    "attributes": {
      "name": [
        [
          {"AttributeValue": "pressure", "AttributeReference": "header"}
        ]
      ],
      "value": [
        [
          {"AttributeValue": "1.2", "AttributeReference": 5}
        ]
      ],
      "error": [
        [
          {"AttributeValue": "0.1", "AttributeReference": 6}
        ]
      ],
      "unit": [
        [
          {"AttributeValue": "pA", "AttributeReference": "header"}
        ]
      ]
    }
  },
  {
    "attributes": {
      "name": [
        [
          {"AttributeValue": "temperature", "AttributeReference": "header"}
        ]
      ],
      "value": [
        [
          {"AttributeValue": "27", "AttributeReference": 7}
        ]
      ],
      "unit": [
        [
          {"AttributeValue": "C", "AttributeReference": "header"}
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
          {"AttributeValue": "Mixing", "AttributeReference": 3}
        ]
      ],
      "identifier": [
        [
          {"AttributeValue": "AS-2001", "AttributeReference": 2}
        ]
      ]
    }
  },
  {
    "attributes": {
      "name": [
        [
          {"AttributeValue": "Spray Coating", "AttributeReference": 8}
        ]
      ]
    }
  }
]"""
    },]

