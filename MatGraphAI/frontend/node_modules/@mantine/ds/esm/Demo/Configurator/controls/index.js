import { BooleanControl } from './BooleanControl.js';
import { SizeControl } from './SizeControl.js';
import { StringControl } from './StringControl.js';
import { ColorControl } from './ColorControl.js';
import { SelectControl } from './SelectControl.js';
import { NumberControl } from './NumberControl.js';
import { SegmentedControl } from './SegmentedControl.js';

const controls = {
  boolean: BooleanControl,
  color: ColorControl,
  select: SelectControl,
  string: StringControl,
  size: SizeControl,
  number: NumberControl,
  segmented: SegmentedControl
};

export default controls;
//# sourceMappingURL=index.js.map
