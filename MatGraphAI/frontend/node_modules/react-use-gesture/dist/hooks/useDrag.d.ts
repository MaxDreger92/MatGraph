import { Handler, HookReturnType, UseDragConfig } from '../types';
/**
 * @public
 *
 * Drag hook.
 *
 * @param {Handler<'drag'>} handler - the function fired every time the drag gesture updates
 * @param {(Config | {})} [config={}] - the config object including generic options and drag options
 * @returns {(...args: any[]) => HookReturnType<Config>}
 */
export declare function useDrag<Config extends UseDragConfig>(handler: Handler<'drag'>, config?: Config | {}): (...args: any[]) => HookReturnType<Config>;
