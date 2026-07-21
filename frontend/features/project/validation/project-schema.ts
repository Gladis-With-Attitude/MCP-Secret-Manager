import { z } from "zod";

const PROJECT_NAME_MIN_LENGTH = 3;
const PROJECT_NAME_MAX_LENGTH = 100;
const PROJECT_DESCRIPTION_MAX_LENGTH = 280;

const projectFormSchema = z.object({
  description: z
    .string()
    .trim()
    .max(
      PROJECT_DESCRIPTION_MAX_LENGTH,
      `Description must contain at most ${PROJECT_DESCRIPTION_MAX_LENGTH} characters.`,
    )
    .optional()
    .or(z.literal("")),
  name: z
    .string()
    .trim()
    .min(
      PROJECT_NAME_MIN_LENGTH,
      `Project name must contain at least ${PROJECT_NAME_MIN_LENGTH} characters.`,
    )
    .max(
      PROJECT_NAME_MAX_LENGTH,
      `Project name must contain at most ${PROJECT_NAME_MAX_LENGTH} characters.`,
    ),
});

type ProjectFormSchemaValues = z.infer<typeof projectFormSchema>;

export {
  PROJECT_DESCRIPTION_MAX_LENGTH,
  PROJECT_NAME_MAX_LENGTH,
  PROJECT_NAME_MIN_LENGTH,
  projectFormSchema,
};
export type { ProjectFormSchemaValues };
