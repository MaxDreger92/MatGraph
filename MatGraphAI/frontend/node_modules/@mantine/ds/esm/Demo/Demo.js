import React from 'react';
import { useMantineTheme } from '@mantine/core';
import CodeDemo from './CodeDemo/CodeDemo.js';
export { default as CodeDemo } from './CodeDemo/CodeDemo.js';
import Configurator from './Configurator/Configurator.js';
export { default as Configurator } from './Configurator/Configurator.js';

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
  const theme = useMantineTheme();
  const background = typeof data.background === "function" ? data.background(theme.colorScheme) : void 0;
  if (data.type === "demo") {
    return /* @__PURE__ */ React.createElement(CodeDemo, __spreadValues(__spreadValues({
      language: "tsx",
      code: data.code || null,
      demoBackground: background
    }, data.demoProps), demoProps), data.wrapper ? /* @__PURE__ */ React.createElement(data.wrapper, null, /* @__PURE__ */ React.createElement(data.component, null)) : /* @__PURE__ */ React.createElement(data.component, null));
  }
  if (data.type === "configurator") {
    return /* @__PURE__ */ React.createElement(Configurator, __spreadValues(__spreadValues({
      component: (props) => data.wrapper ? /* @__PURE__ */ React.createElement(data.wrapper, null, /* @__PURE__ */ React.createElement(data.component, __spreadValues({}, props))) : /* @__PURE__ */ React.createElement(data.component, __spreadValues({}, props)),
      codeTemplate: data.codeTemplate,
      props: data.configurator,
      previewBackground: background
    }, data.configuratorProps), configuratorProps));
  }
  return null;
}

export { Demo };
//# sourceMappingURL=Demo.js.map
