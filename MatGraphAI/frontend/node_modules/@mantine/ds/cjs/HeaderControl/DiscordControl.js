'use strict';

Object.defineProperty(exports, '__esModule', { value: true });

var React = require('react');
var core = require('@mantine/core');
var HeaderControl = require('./HeaderControl.js');
var meta = require('../meta.js');
var DiscordIcon = require('../Icons/DiscordIcon.js');

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
function DiscordControl() {
  return /* @__PURE__ */ React__default.createElement(HeaderControl.HeaderControl, {
    tooltip: "Discord",
    component: "a",
    href: meta.meta.discordLink,
    sx: (theme) => __spreadValues({
      color: theme.white,
      backgroundColor: meta.meta.discordColor,
      borderColor: meta.meta.discordColor
    }, theme.fn.hover({
      backgroundColor: theme.fn.lighten(meta.meta.discordColor, 0.1)
    }))
  }, /* @__PURE__ */ React__default.createElement(DiscordIcon.DiscordIcon, {
    size: core.rem(20)
  }));
}

exports.DiscordControl = DiscordControl;
//# sourceMappingURL=DiscordControl.js.map
