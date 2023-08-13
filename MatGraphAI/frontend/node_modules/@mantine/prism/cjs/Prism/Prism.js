'use strict';

Object.defineProperty(exports, '__esModule', { value: true });

var React = require('react');
var Highlight = require('prism-react-renderer');
var core = require('@mantine/core');
var hooks = require('@mantine/hooks');
var CopyIcon = require('./CopyIcon.js');
var prismTheme = require('./prism-theme.js');
var Prism_styles = require('./Prism.styles.js');

function _interopDefaultLegacy (e) { return e && typeof e === 'object' && 'default' in e ? e['default'] : e; }

var React__default = /*#__PURE__*/_interopDefaultLegacy(React);
var Highlight__default = /*#__PURE__*/_interopDefaultLegacy(Highlight);

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
const prismDefaultProps = {
  noCopy: false,
  copyLabel: "Copy code",
  copiedLabel: "Copied",
  withLineNumbers: false,
  trim: true,
  highlightLines: {},
  scrollAreaComponent: core.ScrollArea,
  getPrismTheme: prismTheme.getPrismTheme
};
const Prism = React.forwardRef((props, ref) => {
  const _a = core.useComponentDefaultProps("Prism", prismDefaultProps, props), {
    className,
    children,
    language,
    noCopy,
    classNames,
    styles,
    copyLabel,
    copiedLabel,
    withLineNumbers,
    highlightLines,
    scrollAreaComponent: ScrollAreaComponent,
    colorScheme,
    trim,
    unstyled,
    radius,
    getPrismTheme,
    variant
  } = _a, others = __objRest(_a, [
    "className",
    "children",
    "language",
    "noCopy",
    "classNames",
    "styles",
    "copyLabel",
    "copiedLabel",
    "withLineNumbers",
    "highlightLines",
    "scrollAreaComponent",
    "colorScheme",
    "trim",
    "unstyled",
    "radius",
    "getPrismTheme",
    "variant"
  ]);
  const code = trim && typeof children === "string" ? children.trim() : children;
  const maxLineSize = code.split("\n").length.toString().length;
  const theme = core.useMantineTheme();
  const clipboard = hooks.useClipboard();
  const _colorScheme = colorScheme || theme.colorScheme;
  const { classes, cx } = Prism_styles['default']({
    colorScheme: _colorScheme,
    native: ScrollAreaComponent !== core.ScrollArea,
    maxLineSize,
    radius
  }, { name: "Prism", classNames, styles, unstyled, variant });
  return /* @__PURE__ */ React__default.createElement(core.Box, __spreadProps(__spreadValues({
    className: cx(classes.root, className),
    ref
  }, others), {
    translate: "no"
  }), !noCopy && /* @__PURE__ */ React__default.createElement(core.Tooltip, {
    label: clipboard.copied ? copiedLabel : copyLabel,
    position: "left",
    withArrow: true,
    arrowSize: 6,
    offset: 6,
    color: clipboard.copied ? "teal" : void 0,
    unstyled
  }, /* @__PURE__ */ React__default.createElement(core.ActionIcon, {
    className: classes.copy,
    "aria-label": clipboard.copied ? copiedLabel : copyLabel,
    onClick: () => clipboard.copy(code),
    unstyled
  }, /* @__PURE__ */ React__default.createElement(CopyIcon.CopyIcon, {
    copied: clipboard.copied
  }))), /* @__PURE__ */ React__default.createElement(Highlight__default, __spreadProps(__spreadValues({}, Highlight.defaultProps), {
    theme: getPrismTheme(theme, _colorScheme),
    code,
    language
  }), ({
    className: inheritedClassName,
    style: inheritedStyle,
    tokens,
    getLineProps,
    getTokenProps
  }) => /* @__PURE__ */ React__default.createElement(ScrollAreaComponent, {
    className: classes.scrollArea,
    dir: "ltr"
  }, /* @__PURE__ */ React__default.createElement("pre", {
    className: cx(classes.code, inheritedClassName),
    style: inheritedStyle,
    dir: "ltr"
  }, tokens.map((line, index) => {
    var _a2, _b, _c, _d;
    if (index === tokens.length - 1 && line.length === 1 && line[0].content === "\n") {
      return null;
    }
    const lineNumber = index + 1;
    const lineProps = getLineProps({ line, key: index });
    const shouldHighlight = lineNumber in highlightLines;
    const lineColor = _colorScheme === "dark" ? theme.fn.rgba(theme.fn.themeColor((_a2 = highlightLines[lineNumber]) == null ? void 0 : _a2.color, 9), 0.25) : theme.fn.themeColor((_b = highlightLines[lineNumber]) == null ? void 0 : _b.color, 0);
    return /* @__PURE__ */ React__default.createElement("div", __spreadProps(__spreadValues({}, lineProps), {
      className: cx(classes.line, lineProps.className),
      style: __spreadValues({}, shouldHighlight ? { backgroundColor: lineColor } : null)
    }), withLineNumbers && /* @__PURE__ */ React__default.createElement("div", {
      className: classes.lineNumber,
      style: {
        color: shouldHighlight ? theme.fn.themeColor((_c = highlightLines[lineNumber]) == null ? void 0 : _c.color, _colorScheme === "dark" ? 5 : 8) : void 0
      }
    }, ((_d = highlightLines[lineNumber]) == null ? void 0 : _d.label) || lineNumber), /* @__PURE__ */ React__default.createElement("div", {
      className: classes.lineContent
    }, line.map((token, key) => {
      var _a3, _b2;
      const tokenProps = getTokenProps({ token, key });
      return /* @__PURE__ */ React__default.createElement("span", __spreadProps(__spreadValues({}, tokenProps), {
        style: __spreadProps(__spreadValues({}, tokenProps.style), {
          color: shouldHighlight ? theme.fn.themeColor((_a3 = highlightLines[lineNumber]) == null ? void 0 : _a3.color, _colorScheme === "dark" ? 5 : 8) : (_b2 = tokenProps == null ? void 0 : tokenProps.style) == null ? void 0 : _b2.color
        })
      }));
    })));
  }).filter(Boolean)))));
});
Prism.displayName = "@mantine/prism/Prism";

exports.Prism = Prism;
//# sourceMappingURL=Prism.js.map
