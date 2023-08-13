import React from 'react';
import { rem } from '@mantine/core';
import { IconTextDirectionLtr, IconTextDirectionRtl } from '@tabler/icons-react';
import { HeaderControl } from './HeaderControl.js';

function DirectionControl({ direction, toggleDirection }) {
  return /* @__PURE__ */ React.createElement(HeaderControl, {
    onClick: () => toggleDirection(),
    tooltip: `${direction === "ltr" ? "RTL" : "LTR"} direction`
  }, direction === "rtl" ? /* @__PURE__ */ React.createElement(IconTextDirectionLtr, {
    size: rem(22),
    stroke: 1.5
  }) : /* @__PURE__ */ React.createElement(IconTextDirectionRtl, {
    size: rem(22),
    stroke: 1.5
  }));
}

export { DirectionControl };
//# sourceMappingURL=DirectionControl.js.map
