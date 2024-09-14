import { z } from 'zod';
import { ILabware } from '../types/labware.types';

const WellSchema = z.object({
  depth: z.number(),
  totalLiquidVolume: z.number(),
  shape: z.string(),
  diameter: z.number().optional(),
  xDimension: z.number().optional(),
  yDimension: z.number().optional(),
  x: z.number(),
  y: z.number(),
  z: z.number(),
});

const MetadataSchema = z.object({
  displayName: z.string(),
  displayCategory: z.string(),
  displayVolumeUnits: z.string(),
  tags: z.array(z.string()),
});

const DimensionsSchema = z.object({
  xDimension: z.number(),
  yDimension: z.number(),
  zDimension: z.number(),
});

const GroupMetadataSchema = z.object({
  wellBottomShape: z.string().optional(),
});

const GroupSchema = z.object({
  metadata: GroupMetadataSchema,
  wells: z.array(z.string()),
});

const LabwareParametersSchema = z.object({
  format: z.string(),
  quirks: z.array(z.string()),
  isMagneticModuleCompatible: z.boolean(),
  loadName: z.string(),
  tipLength: z.number().optional(),
});

const CornerOffsetFromSlotSchema = z.object({
  x: z.number(),
  y: z.number(),
  z: z.number(),
});

const BrandSchema = z.object({
  brand: z.string(),
  brandId: z.array(z.string()),
});

const ILabwareSchema = z.object({
  ordering: z.array(z.array(z.string())),
  brand: BrandSchema,
  metadata: MetadataSchema,
  dimensions: DimensionsSchema,
  wells: z.record(WellSchema),
  groups: z.array(GroupSchema),
  parameters: LabwareParametersSchema,
  namespace: z.string(),
  version: z.number(),
  schemaVersion: z.number(),
  cornerOffsetFromSlot: CornerOffsetFromSlotSchema,
});

export function isILabware(data: any): data is ILabware {
  try {
    ILabwareSchema.parse(data);
    return true;
  } catch (e) {
    console.error('Invalid labware data:', e);
    return false;
  }
}
