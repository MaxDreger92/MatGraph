import React from 'react';
import { Switch } from '@mantine/core';
import { upperFirst } from '@mantine/hooks';

var __defProp = Object.defineProperty;
var __defProps = Object.defineProperties;
var __getOwnPropDescs = Object.getOwnPropertyDescriptors;
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
var __spreadProps = (a, b) => __defProps(a, __getOwnPropDescs(b));
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
const splitCamelCase = (string) => {
  const splitted = string.replace(/([a-z0-9])([A-Z])/g, "$1 $2").toLowerCase();
  return upperFirst(splitted);
};
function BooleanControl(_a) {
  var _b = _a, { value, label, onChange } = _b, others = __objRest(_b, ["value", "label", "onChange"]);
  return /* @__PURE__ */ React.createElement(Switch, __spreadProps(__spreadValues({}, others), {
    size: "sm",
    label: splitCamelCase(label),
    checked: value,
    onChange: (event) => onChange(event.currentTarget.checked)
  }));
}
BooleanControl.initialValue = false;

export { BooleanControl };
//# sourceMappingURL=BooleanControl.js.map
