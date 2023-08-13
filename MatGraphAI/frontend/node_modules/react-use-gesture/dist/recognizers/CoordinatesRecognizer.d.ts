import Recognizer from './Recognizer';
import { Vector2, UseGestureEvent, PartialGestureState, FalseOrNumber, GestureState, CoordinatesKey } from '../types';
/**
 * @private
 * Abstract class for coordinates-based gesture recongizers
 * @abstract
 * @class CoordinatesRecognizer
 * @extends {Recognizer<T>}
 * @template T
 */
export default abstract class CoordinatesRecognizer<T extends CoordinatesKey> extends Recognizer<T> {
    /**
     * Returns the real movement (without taking intentionality into acount)
     */
    protected getInternalMovement(values: Vector2, state: GestureState<T>): Vector2;
    /**
     * In coordinates-based gesture, this function will detect the first intentional axis,
     * lock the gesture axis if lockDirection is specified in the config, block the gesture
     * if the first intentional axis doesn't match the specified axis in config.
     *
     * @param {[FalseOrNumber, FalseOrNumber]} _intentional
     * @param {Vector2} _movement
     * @param {PartialGestureState<T>} state
     */
    protected checkIntentionality(_intentional: [FalseOrNumber, FalseOrNumber], _movement: Vector2, state: PartialGestureState<T>): PartialGestureState<T>;
    getKinematics(values: Vector2, event: UseGestureEvent): PartialGestureState<T>;
    protected mapStateValues(state: GestureState<T>): PartialGestureState<T>;
}
