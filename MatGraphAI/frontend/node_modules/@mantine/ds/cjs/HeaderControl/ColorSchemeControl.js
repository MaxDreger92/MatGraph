'use strict';

Object.defineProperty(exports, '__esModule', { value: true });

var React = require('react');
var core = require('@mantine/core');
var iconsReact = require('@tabler/icons-react');
var HeaderControl = require('./HeaderControl.js');

function _interopDefaultLegacy (e) { return e && typeof e === 'object' && 'default' in e ? e['default'] : e; }

var React__default = /*#__PURE__*/_interopDefaultLegacy(React);

function ColorSchemeControl() {
  const { colorScheme, toggleColorScheme } = core.useMantineColorScheme();
  return /* @__PURE__ */ React__default.createElement(HeaderControl.HeaderControl, {
    onClick: () => toggleColorScheme(),
    tooltip: `${colorScheme === "dark" ? "Light" : "Dark"} mode`
  }, colorScheme === "dark" ? /* @__PURE__ */ React__default.createElement(iconsReact.IconSun, {
    size: core.rem(22),
    stroke: 1.5
  }) : /* @__PURE__ */ React__default.createElement(iconsReact.IconMoon, {
    size: core.rem(22),
    stroke: 1.5
  }));
}

exports.ColorSchemeControl = ColorSchemeControl;
//# sourceMappingURL=ColorSchemeControl.js.map
