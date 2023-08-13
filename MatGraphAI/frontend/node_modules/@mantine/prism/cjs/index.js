'use strict';

Object.defineProperty(exports, '__esModule', { value: true });

var core = require('@mantine/core');
var PrismTabs = require('./PrismTabs/PrismTabs.js');
var Prism = require('./Prism/Prism.js');

const PrismExport = Prism.Prism;
PrismExport.Tabs = PrismTabs.PrismTabs;
PrismExport.Tab = core.Tabs.Tab;
PrismExport.TabsList = core.Tabs.List;
PrismExport.Panel = PrismTabs.PrismPanel;

exports.Prism = PrismExport;
//# sourceMappingURL=index.js.map
