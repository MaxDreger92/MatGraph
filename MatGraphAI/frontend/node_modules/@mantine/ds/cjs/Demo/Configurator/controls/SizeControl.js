'use strict';

Object.defineProperty(exports, '__esModule', { value: true });

var React = require('react');
var core = require('@mantine/core');
var hooks = require('@mantine/hooks');

function _interopDefaultLegacy (e) { return e && typeof e === 'object' && 'default' in e ? e['default'] : e; }

var React__default = /*#__PURE__*/_interopDefaultLegacy(React);

var __defProp = Object.defineProperty;
var __getOwnPropSymbols = Object.getOwnPropertySymbols;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __propIsEnum = Object.prototype.propertyIsEnumerable;
var __defNormalProp = (obj, key, value) => key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value;
var __spreadValues = (a, b) => {
  for (var prop in b || (b = {}))
    if (__hasOwnProp.call(b, prop))
      __defNormalProp(a, prop, b[prop]);
  if (__getOwnPropSymbols)
    for (var prop of __getOwnPropSymbols(b)) {
      if (__propIsEnum.call(b, prop))
        __defNormalProp(a, prop, b[prop]);
    }
  return a;
};
var __objRest = (source, exclude) => {
  var target = {};
  for (var prop in source)
    if (__hasOwnProp.call(source, prop) && exclude.indexOf(prop) < 0)
      target[prop] = source[prop];
  if (source != null && __getOwnPropSymbols)
    for (var prop of __getOwnPropSymbols(source)) {
      if (exclude.indexOf(prop) < 0 && __propIsEnum.call(source, prop))
        target[prop] = source[prop];
    }
  return target;
};
const MARKS = [
  { value: 0, label: "xs" },
  { value: 25, label: "sm" },
  { value: 50, label: "md" },
  { value: 75, label: "lg" },
  { value: 100, label: "xl" }
];
function SizeControl(_a) {
  var _b = _a, { label, value, onChange, step = 25 } = _b, others = __objRest(_b, ["label", "value", "onChange", "step"]);
  const _value = MARKS.find((mark) => mark.label === value).value;
  const handleChange = (val) => onChange(MARKS.find((mark) => mark.value === val).label);
  return /* @__PURE__ */ React__default.createElement(core.Input.Wrapper, __spreadValues({
    labelElement: "div",
    label: hooks.upperFirst(label)
  }, others), /* @__PURE__ */ React__default.createElement(core.Slider, {
    value: _value,
    onChange: handleChange,
    label: (val) => MARKS.find((mark) => mark.value === val).label,
    step,
    marks: MARKS,
    styles: { markLabel: { display: "none" } }
  }));
}
SizeControl.initialValue = "md";

exports.SizeControl = SizeControl;
//# sourceMappingURL=SizeControl.js.map
