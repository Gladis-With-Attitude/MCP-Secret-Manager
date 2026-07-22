"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import type { Resolver } from "react-hook-form";
import { useForm } from "react-hook-form";

import { Button } from "@/components/buttons/button";
import { FormField } from "@/components/forms/form-field";
import { Input } from "@/components/forms/input";
import { Select } from "@/components/forms/select";
import { Grid } from "@/components/layout/grid";
import { Stack } from "@/components/layout/stack";

import { mapAuditFilterFormToFilters } from "../mappers/audit-mappers";
import type { AuditFilterFormValues, AuditFilters as AuditFilterState } from "../types/audit";
import { auditFiltersSchema, type AuditFiltersSchemaValues } from "../validation/audit-schema";
import { AuditSearch } from "./audit-search";

type AuditFiltersProps = {
  defaultValues: AuditFilterFormValues;
  filters: AuditFilterState;
  onApply: (filters: AuditFilterState) => void;
  onReset: () => void;
};

const resultOptions = [
  { label: "All results", value: "all" },
  { label: "Success", value: "success" },
  { label: "Failure", value: "failure" },
];

function AuditFilters({ defaultValues, filters, onApply, onReset }: AuditFiltersProps) {
  const {
    formState: { errors },
    handleSubmit,
    register,
    setValue,
    watch,
  } = useForm<AuditFiltersSchemaValues>({
    defaultValues,
    resolver: zodResolver(auditFiltersSchema) as Resolver<AuditFiltersSchemaValues>,
    values: defaultValues,
  });
  const result = watch("result");
  const query = watch("query") ?? "";

  function handleValidSubmit(values: AuditFiltersSchemaValues) {
    onApply(mapAuditFilterFormToFilters(values, filters));
  }

  return (
    <form
      className="w-full"
      onSubmit={(event) => {
        void handleSubmit(handleValidSubmit)(event);
      }}
    >
      <Stack>
        <AuditSearch
          error={errors.query?.message}
          onChange={(value) => setValue("query", value)}
          value={query}
        />
        <Grid columns={3}>
          <FormField error={errors.actorId?.message} id="audit-actor" label="Actor">
            <Input
              aria-invalid={Boolean(errors.actorId)}
              id="audit-actor"
              placeholder="actor id"
              {...register("actorId")}
            />
          </FormField>
          <FormField error={errors.action?.message} id="audit-action" label="Action">
            <Input
              aria-invalid={Boolean(errors.action)}
              id="audit-action"
              placeholder="secret.read"
              {...register("action")}
            />
          </FormField>
          <FormField error={errors.result?.message} id="audit-result" label="Result">
            <Select
              id="audit-result"
              onValueChange={(value) =>
                setValue("result", value as AuditFiltersSchemaValues["result"])
              }
              options={resultOptions}
              value={result}
            />
          </FormField>
          <FormField
            error={errors.resourceType?.message}
            id="audit-resource-type"
            label="Resource type"
          >
            <Input
              aria-invalid={Boolean(errors.resourceType)}
              id="audit-resource-type"
              placeholder="secret"
              {...register("resourceType")}
            />
          </FormField>
          <FormField error={errors.resourceId?.message} id="audit-resource-id" label="Resource ID">
            <Input
              aria-invalid={Boolean(errors.resourceId)}
              id="audit-resource-id"
              placeholder="resource id"
              {...register("resourceId")}
            />
          </FormField>
          <FormField error={errors.startDate?.message} id="audit-start-date" label="Start date">
            <Input id="audit-start-date" type="datetime-local" {...register("startDate")} />
          </FormField>
          <FormField error={errors.endDate?.message} id="audit-end-date" label="End date">
            <Input id="audit-end-date" type="datetime-local" {...register("endDate")} />
          </FormField>
        </Grid>
        <div className="flex flex-wrap justify-end gap-2">
          <Button onClick={onReset} variant="outline">
            Reset filters
          </Button>
          <Button type="submit">Apply filters</Button>
        </div>
      </Stack>
    </form>
  );
}

export { AuditFilters };
export type { AuditFiltersProps };
