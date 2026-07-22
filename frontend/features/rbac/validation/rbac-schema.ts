import { z } from "zod";

const RBAC_DEFAULT_LIMIT = 20;
const RBAC_MAX_LIMIT = 100;

const roleNameSchema = z
  .string()
  .trim()
  .min(3, "Role name must contain at least 3 characters.")
  .max(80, "Role name must contain at most 80 characters.")
  .regex(
    /^[a-z][a-z0-9_.:-]*$/,
    "Use lowercase letters, numbers, dots, underscores, colons or hyphens.",
  );

const roleFormSchema = z.object({
  description: z
    .string()
    .max(280, "Description must contain at most 280 characters.")
    .optional()
    .or(z.literal("")),
  name: roleNameSchema,
  permissionIds: z.array(z.string().min(1)).min(1, "Select at least one permission."),
});

const roleFilterSchema = z.object({
  kind: z.enum(["all", "custom", "system"]).default("all"),
  query: z.string().max(120).optional().or(z.literal("")),
  status: z.enum(["all", "active", "inactive"]).default("all"),
});

const roleAssignmentSchema = z.object({
  actorId: z
    .string()
    .trim()
    .min(1, "Actor ID is required.")
    .max(120, "Actor ID must contain at most 120 characters."),
  roleId: z.string().trim().min(1, "Role is required."),
});

type RoleAssignmentSchemaValues = z.infer<typeof roleAssignmentSchema>;
type RoleFilterSchemaValues = z.infer<typeof roleFilterSchema>;
type RoleFormSchemaValues = z.infer<typeof roleFormSchema>;

export {
  RBAC_DEFAULT_LIMIT,
  RBAC_MAX_LIMIT,
  roleAssignmentSchema,
  roleFilterSchema,
  roleFormSchema,
  roleNameSchema,
};
export type { RoleAssignmentSchemaValues, RoleFilterSchemaValues, RoleFormSchemaValues };
