'use strict';

Object.defineProperty(exports, '__esModule', { value: true });

var React = require('react');
var core = require('@mantine/core');
var CodeDemo = require('./CodeDemo/CodeDemo.js');
var Configurator = require('./Configurator/Configurator.js');

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
function Demo({ data, demoProps, configuratorProps }) {
  const theme = core.useMantineTheme();
  const background = typeof data.background === "function" ? data.background(theme.colorScheme) : void 0;
  if (data.type === "demo") {
    return /* @__PURE__ */ React__default.createElement(CodeDemo['default'], __spreadValues(__spreadValues({
      language: "tsx",
      code: data.code || null,
      demoBackground: background
    }, data.demoProps), demoProps), data.wrapper ? /* @__PURE__ */ React__default.createElement(data.wrapper, null, /* @__PURE__ */ React__default.createElement(data.component, null)) : /* @__PURE__ */ React__default.createElement(data.component, null));
  }
  if (data.type === "configurator") {
    return /* @__PURE__ */ React__default.createElement(Configurator['default'], __spreadValues(__spreadValues({
      component: (props) => data.wrapper ? /* @__PURE__ */ React__default.createElement(data.wrapper, null, /* @__PURE__ */ React__default.createElement(data.component, __spreadValues({}, props))) : /* @__PURE__ */ React__default.createElement(data.component, __spreadValues({}, props)),
      codeTemplate: data.codeTemplate,
      props: data.configurator,
      previewBackground: background
    }, data.configuratorProps), configuratorProps));
  }
  return null;
}

exports.CodeDemo = CodeDemo['default'];
exports.Configurator = Configurator['default'];
exports.Demo = Demo;
//# sourceMappingURL=Demo.js.map
