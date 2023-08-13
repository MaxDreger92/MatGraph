'use strict';

Object.defineProperty(exports, '__esModule', { value: true });

var React = require('react');
var core = require('@mantine/core');
var iconsReact = require('@tabler/icons-react');
var HeaderControl = require('./HeaderControl.js');

function _interopDefaultLegacy (e) { return e && typeof e === 'object' && 'default' in e ? e['default'] : e; }

var React__default = /*#__PURE__*/_interopDefaultLegacy(React);

function DirectionControl({ direction, toggleDirection }) {
  return /* @__PURE__ */ React__default.createElement(HeaderControl.HeaderControl, {
    onClick: () => toggleDirection(),
    tooltip: `${direction === "ltr" ? "RTL" : "LTR"} direction`
  }, direction === "rtl" ? /* @__PURE__ */ React__default.createElement(iconsReact.IconTextDirectionLtr, {
    size: core.rem(22),
    stroke: 1.5
  }) : /* @__PURE__ */ React__default.createElement(iconsReact.IconTextDirectionRtl, {
    size: core.rem(22),
    stroke: 1.5
  }));
}

exports.DirectionControl = DirectionControl;
//# sourceMappingURL=DirectionControl.js.map
