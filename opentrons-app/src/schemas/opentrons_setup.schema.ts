import { z } from 'zod';
import { OpentronsSetup } from '../types/opentrons.types';

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
  labware: z.array(LabwareSchema), 
  pipettes: z.array(PipetteSchema).optional(),
});

export function isOpentronsSetup(data: any): data is OpentronsSetup {
    try {
      OpentronsSetupSchema.parse(data);
      return true;
    } catch (e) {
      console.error('Invalid opentrons setup data:', e);
      return false;
    }
  }
  
