import React from 'react';
import { Button, rem } from '@mantine/core';
import { packSx } from '@mantine/utils';
import { meta } from '../meta.js';
import { DiscordIcon } from '../Icons/DiscordIcon.js';
import { TwitterIcon } from '../Icons/TwitterIcon.js';

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
function SocialButton(_a) {
  var _b = _a, { icon } = _b, others = __objRest(_b, ["icon"]);
  return /* @__PURE__ */ React.createElement(Button, __spreadValues({
    component: "a",
    target: "_blank",
    rel: "noopener noreferrer",
    leftIcon: icon,
    styles: (theme) => ({
      root: {
        border: 0,
        height: rem(42),
        paddingLeft: rem(20),
        paddingRight: rem(20)
      },
      leftIcon: {
        marginRight: theme.spacing.md
      }
    })
  }, others));
}
function DiscordButton(_c) {
  var _d = _c, { sx } = _d, others = __objRest(_d, ["sx"]);
  return /* @__PURE__ */ React.createElement(SocialButton, __spreadValues({
    sx: [
      (theme) => __spreadValues({
        backgroundColor: meta.discordColor
      }, theme.fn.hover({ backgroundColor: theme.fn.lighten(meta.discordColor, 0.1) })),
      ...packSx(sx)
    ],
    icon: /* @__PURE__ */ React.createElement(DiscordIcon, {
      size: 16
    }),
    href: meta.discordLink
  }, others), "Join Discord community");
}
function TwitterButton(_e) {
  var _f = _e, { sx } = _f, others = __objRest(_f, ["sx"]);
  return /* @__PURE__ */ React.createElement(SocialButton, __spreadValues({
    sx: [
      (theme) => __spreadValues({
        backgroundColor: meta.twitterColor
      }, theme.fn.hover({ backgroundColor: theme.fn.lighten(meta.twitterColor, 0.1) })),
      ...packSx(sx)
    ],
    icon: /* @__PURE__ */ React.createElement(TwitterIcon, {
      size: 16
    }),
    href: meta.twitterLink
  }, others), "Follow Mantine on Twitter");
}

export { DiscordButton, SocialButton, TwitterButton };
//# sourceMappingURL=SocialButton.js.map
