import Recognizer from './Recognizer';
import { Vector2, UseGestureEvent, PartialGestureState, DistanceAngleKey, GestureState } from '../types';
/**
 * @private
 * Abstract class for distance/angle-based gesture recongizers
 * @abstract
 * @class DistanceAngleRecognizer
 * @extends {Recognizer<T>}
 * @template T
 */
export default abstract class DistanceAngleRecognizer<T extends DistanceAngleKey> extends Recognizer<T> {
    /**
     * Returns the real movement (without taking intentionality into acount)
     */
    protected getInternalMovement([d, a]: [number, number?], state: GestureState<T>): Vector2;
    getKinematics(values: Vector2, event: UseGestureEvent): PartialGestureState<T>;
    protected mapStateValues(state: GestureState<T>): PartialGestureState<T>;
}
