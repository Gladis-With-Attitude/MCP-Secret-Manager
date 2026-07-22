import { z } from "zod";

const AUDIT_NAME_PATTERN = /^[a-z][a-z0-9_.:-]*$/;
const AUDIT_ID_MAX_LENGTH = 128;
const AUDIT_QUERY_MAX_LENGTH = 160;
const AUDIT_DEFAULT_LIMIT = 100;
const AUDIT_MAX_LIMIT = 500;

const auditResultOptions = ["all", "success", "failure"] as const;

const auditOptionalNameSchema = z
  .string()
  .trim()
  .max(AUDIT_ID_MAX_LENGTH, `Value must contain at most ${AUDIT_ID_MAX_LENGTH} characters.`)
  .refine((value) => !value || AUDIT_NAME_PATTERN.test(value), {
    message: "Use lowercase letters, numbers, underscore, dot, colon or dash.",
  })
  .optional()
  .or(z.literal(""));

const auditFiltersSchema = z
  .object({
    action: auditOptionalNameSchema,
    actorId: z
      .string()
      .trim()
      .max(AUDIT_ID_MAX_LENGTH, `Actor id must contain at most ${AUDIT_ID_MAX_LENGTH} characters.`)
      .optional()
      .or(z.literal("")),
    endDate: z.string().optional().or(z.literal("")),
    query: z
      .string()
      .trim()
      .max(
        AUDIT_QUERY_MAX_LENGTH,
        `Search must contain at most ${AUDIT_QUERY_MAX_LENGTH} characters.`,
      )
      .optional()
      .or(z.literal("")),
    resourceId: z
      .string()
      .trim()
      .max(
        AUDIT_ID_MAX_LENGTH,
        `Resource id must contain at most ${AUDIT_ID_MAX_LENGTH} characters.`,
      )
      .optional()
      .or(z.literal("")),
    resourceType: auditOptionalNameSchema,
    result: z.enum(auditResultOptions),
    startDate: z.string().optional().or(z.literal("")),
  })
  .refine(
    (values) => {
      if (!values.startDate || !values.endDate) {
        return true;
      }

      return Date.parse(values.startDate) <= Date.parse(values.endDate);
    },
    { message: "Start date must be before end date.", path: ["endDate"] },
  );

type AuditFiltersSchemaValues = z.infer<typeof auditFiltersSchema>;

export {
  AUDIT_DEFAULT_LIMIT,
  AUDIT_MAX_LIMIT,
  AUDIT_NAME_PATTERN,
  auditFiltersSchema,
  auditResultOptions,
};
export type { AuditFiltersSchemaValues };
