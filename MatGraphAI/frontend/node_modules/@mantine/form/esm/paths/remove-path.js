import { getPath } from './get-path.js';
import { setPath } from './set-path.js';

function removePath(path, index, values) {
  const currentValue = getPath(path, values);
  if (!Array.isArray(currentValue)) {
    return values;
  }
  return setPath(path, currentValue.filter((_, itemIndex) => itemIndex !== index), values);
}

export { removePath };
//# sourceMappingURL=remove-path.js.map
