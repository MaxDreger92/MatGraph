import { z } from 'zod';
import { ChemicalSetup, Configuration, OpentronsSetup } from '../types/configuration.types';

const OpentronsLocationSchema = z.object({
    slot: z.number(),
    well: z.string(),
});

const ArduinoLocationSchema = z.object({
    pump: z.string(),
    type: z.string(),
});

const VolumeSchema = z.object({
    value: z.number(),
    unit: z.string(),
});

const OpentronsChemicalSchema = z.object({
    location: OpentronsLocationSchema,
    name: z.string(),
    volume: VolumeSchema,
});

const ArduinoChemicalSchema = z.object({
    location: ArduinoLocationSchema,
    name: z.string(),
    volume: VolumeSchema,
});

const ChemicalSetupSchema = z.object({
    name: z.string().optional(),
    opentrons: z.array(OpentronsChemicalSchema),
    arduino: z.array(ArduinoChemicalSchema),
});

const LabwareSchema = z.object({
    slot: z.number(),
    name: z.string(),
    filename: z.string(),
    namespace: z.string(),
    version: z.number(),
    intent: z.string(),
});

const PipetteSchema = z.object({
    mount: z.string(),
    name: z.string(),
    intent: z.string(),
});

const OpentronsSetupSchema = z.object({
    name: z.string().optional(),
    labware: z.array(LabwareSchema),
    pipettes: z.array(PipetteSchema).optional(),
});

const ConfigurationSchema = z.object({
    deckSetup: OpentronsSetupSchema,
    chemicalSetup: ChemicalSetupSchema,
});

export const isConfiguration = (data: unknown): data is Configuration => {
    const result = ConfigurationSchema.safeParse(data);
    if (!result.success) {
        console.error('Invalid configuration:', result.error.format());
    }
    return result.success;
};

export const isPartialConfiguration = (data: unknown): data is Partial<Configuration> => {
    const partialSchema = ConfigurationSchema.partial();
    const result = partialSchema.safeParse(data);
    if (!result.success) {
        console.error('Invalid partial configuration:', result.error.format());
    }
    return result.success;
};

export const isOpentronsSetup = (data: unknown): data is OpentronsSetup | OpentronsSetup[] => {
    if (!data) return false;

    const dataList = Array.isArray(data) ? data : [data];

    for (const item of dataList) {
        const result = OpentronsSetupSchema.safeParse(item);
        if (!result.success) {
            console.error('Invalid opentrons setup data:', result.error.format());
            return false;
        }
    }

    return true;
};

export const isChemicalSetup = (data: unknown): data is ChemicalSetup | ChemicalSetup[] => {
    if (!data) return false;

    const dataList = Array.isArray(data) ? data : [data];

    for (const item of dataList) {
        const result = ChemicalSetupSchema.safeParse(item);
        if (!result.success) {
            console.error('Invalid chemicals setup data:', result.error.format());
            return false;
        }
    }

    return true;
};
