'use strict';

Object.defineProperty(exports, '__esModule', { value: true });

var BooleanControl = require('./BooleanControl.js');
var SizeControl = require('./SizeControl.js');
var StringControl = require('./StringControl.js');
var ColorControl = require('./ColorControl.js');
var SelectControl = require('./SelectControl.js');
var NumberControl = require('./NumberControl.js');
var SegmentedControl = require('./SegmentedControl.js');

const controls = {
  boolean: BooleanControl.BooleanControl,
  color: ColorControl.ColorControl,
  select: SelectControl.SelectControl,
  string: StringControl.StringControl,
  size: SizeControl.SizeControl,
  number: NumberControl.NumberControl,
  segmented: SegmentedControl.SegmentedControl
};

exports.default = controls;
//# sourceMappingURL=index.js.map
