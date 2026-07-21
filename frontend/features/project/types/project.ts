type ProjectStatus = "active" | "archived";

type ProjectPermission = "archive" | "create" | "delete" | "read" | "update";

type ProjectPermissions = Partial<Record<ProjectPermission, boolean>>;

type Project = {
  archived: boolean;
  createdAt?: string | null;
  createdBy?: string | null;
  description?: string | null;
  id: string;
  name: string;
  permissions: ProjectPermissions;
  secretCount?: number | null;
  status: ProjectStatus;
  updatedAt?: string | null;
  vaultId: string;
  vaultName?: string | null;
  versionCount?: number | null;
};

type ProjectListFilters = {
  archived?: boolean;
  page?: number;
  pageSize?: number;
  search?: string;
  status?: ProjectStatus | "all";
};

type ProjectList = {
  items: Project[];
  pagination: {
    hasNextPage?: boolean;
    hasPreviousPage?: boolean;
    page?: number;
    pageSize?: number;
    total?: number;
  };
  permissions: ProjectPermissions;
  vaultId: string;
};

type ProjectFormValues = {
  description?: string;
  name: string;
};

export type {
  Project,
  ProjectFormValues,
  ProjectList,
  ProjectListFilters,
  ProjectPermission,
  ProjectPermissions,
  ProjectStatus,
};
