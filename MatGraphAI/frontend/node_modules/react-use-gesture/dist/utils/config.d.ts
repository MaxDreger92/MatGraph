import { GenericOptions, InternalGenericOptions, DragConfig, GestureOptions, InternalDragOptions, InternalGestureOptions, CoordinatesConfig, InternalCoordinatesOptions, DistanceAngleConfig, InternalDistanceAngleOptions } from '../types';
/**
 * @private
 *
 * Returns the internal generic option object.
 *
 * @param {Partial<GenericOptions>} [config={}]
 * @returns {InternalGenericOptions}
 */
export declare function getInternalGenericOptions(config?: Partial<GenericOptions>): InternalGenericOptions;
export declare function getInternalGestureOptions(gestureConfig: Partial<GestureOptions>): InternalGestureOptions;
export declare function getInternalCoordinatesOptions(coordinatesConfig?: CoordinatesConfig): InternalCoordinatesOptions;
export declare function getInternalDistanceAngleOptions(distanceAngleConfig?: DistanceAngleConfig): InternalDistanceAngleOptions;
export declare function getInternalDragOptions(dragConfig?: DragConfig): InternalDragOptions;
