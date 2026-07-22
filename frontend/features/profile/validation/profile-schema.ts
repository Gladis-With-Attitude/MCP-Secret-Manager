import { z } from "zod";

const profileFormSchema = z.object({
  email: z.string().email("Enter a valid email address.").optional().or(z.literal("")),
  name: z
    .string()
    .trim()
    .min(2, "Name must contain at least 2 characters.")
    .max(120, "Name must contain at most 120 characters."),
  organization: z
    .string()
    .trim()
    .max(120, "Organization must contain at most 120 characters.")
    .optional()
    .or(z.literal("")),
});

const changePasswordSchema = z
  .object({
    currentPassword: z.string().min(1, "Current password is required."),
    newPassword: z
      .string()
      .min(12, "New password must contain at least 12 characters.")
      .max(128, "New password must contain at most 128 characters."),
  })
  .refine((values) => values.currentPassword !== values.newPassword, {
    message: "New password must be different from the current password.",
    path: ["newPassword"],
  });

type ChangePasswordSchemaValues = z.infer<typeof changePasswordSchema>;
type ProfileFormSchemaValues = z.infer<typeof profileFormSchema>;

export { changePasswordSchema, profileFormSchema };
export type { ChangePasswordSchemaValues, ProfileFormSchemaValues };
