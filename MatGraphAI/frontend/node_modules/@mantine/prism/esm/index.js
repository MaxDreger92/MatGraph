import { Tabs } from '@mantine/core';
import { PrismTabs, PrismPanel } from './PrismTabs/PrismTabs.js';
import { Prism } from './Prism/Prism.js';

const PrismExport = Prism;
PrismExport.Tabs = PrismTabs;
PrismExport.Tab = Tabs.Tab;
PrismExport.TabsList = Tabs.List;
PrismExport.Panel = PrismPanel;

export { PrismExport as Prism };
//# sourceMappingURL=index.js.map
