import React from 'react';
import { Tooltip, Group } from '@mantine/core';
import { ColorSchemeControl } from './ColorSchemeControl.js';
import { DirectionControl } from './DirectionControl.js';
import { GithubControl } from './GithubControl.js';
import { DiscordControl } from './DiscordControl.js';
import { SearchControl } from '../SearchControl/SearchControl.js';

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
function HeaderControls(_a) {
  var _b = _a, {
    onSearch,
    githubLink,
    direction,
    toggleDirection
  } = _b, others = __objRest(_b, [
    "onSearch",
    "githubLink",
    "direction",
    "toggleDirection"
  ]);
  return /* @__PURE__ */ React.createElement(Tooltip.Group, {
    openDelay: 600,
    closeDelay: 100
  }, /* @__PURE__ */ React.createElement(Group, __spreadValues({
    spacing: "xs"
  }, others), /* @__PURE__ */ React.createElement(SearchControl, {
    onClick: onSearch
  }), /* @__PURE__ */ React.createElement(DiscordControl, null), /* @__PURE__ */ React.createElement(GithubControl, {
    link: githubLink
  }), /* @__PURE__ */ React.createElement(DirectionControl, {
    direction,
    toggleDirection
  }), /* @__PURE__ */ React.createElement(ColorSchemeControl, null)));
}

export { HeaderControls };
//# sourceMappingURL=HeaderControls.js.map
