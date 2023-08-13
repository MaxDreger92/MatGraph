import React from 'react';
import { rem } from '@mantine/core';
import { HeaderControl } from './HeaderControl.js';
import { GithubIcon } from '../Icons/GithubIcon.js';

function GithubControl({ link }) {
  return /* @__PURE__ */ React.createElement(HeaderControl, {
    tooltip: "Source code",
    component: "a",
    href: link
  }, /* @__PURE__ */ React.createElement(GithubIcon, {
    size: rem(22)
  }));
}

export { GithubControl };
//# sourceMappingURL=GithubControl.js.map
