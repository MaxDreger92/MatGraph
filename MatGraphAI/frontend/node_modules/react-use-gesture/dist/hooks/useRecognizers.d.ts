import { InternalConfig, HookReturnType, InternalHandlers, RecognizerClasses, GenericOptions, NativeHandlersPartial } from '../types';
/**
 * @private
 *
 * Utility hook called by all gesture hooks and that will be responsible for the internals.
 *
 * @param {Partial<InternalHandlers>} handlers
 * @param {RecognizerClasses} classes
 * @param {InternalConfig} config
 * @param {NativeHandlersPartial} nativeHandlers - native handlers such as onClick, onMouseDown, etc.
 * @returns {(...args: any[]) => HookReturnType<Config>}
 */
export default function useRecognizers<Config extends Partial<GenericOptions>>(handlers: Partial<InternalHandlers>, classes: RecognizerClasses, config: InternalConfig, nativeHandlers?: NativeHandlersPartial): (...args: any[]) => HookReturnType<Config>;
