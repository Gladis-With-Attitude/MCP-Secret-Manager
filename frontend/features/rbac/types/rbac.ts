type RoleKind = "custom" | "system";

type RoleStatus = "active" | "inactive";

type RbacAction = "assign" | "create" | "read" | "revoke" | "update";

type RbacActionPermissions = Partial<Record<RbacAction, boolean>>;

type PermissionSensitivity = "critical" | "standard";

type Permission = {
  action: string;
  description?: string;
  group: string;
  id: string;
  name: string;
  resource: string;
  sensitivity: PermissionSensitivity;
};

type Role = {
  assignmentsCount: number;
  createdAt?: string;
  description?: string;
  id: string;
  kind: RoleKind;
  name: string;
  permissionIds: string[];
  permissions: Permission[];
  permissionsCount: number;
  status: RoleStatus;
  updatedAt?: string;
  uiPermissions: RbacActionPermissions;
};

type RoleList = {
  items: Role[];
  pagination?: {
    hasNextPage: boolean;
    hasPreviousPage: boolean;
    limit: number;
    offset: number;
    total?: number;
  };
  permissions: RbacActionPermissions;
};

type RoleFilters = {
  kind?: "all" | RoleKind;
  limit?: number;
  offset?: number;
  query?: string;
  status?: "all" | RoleStatus;
};

type RoleFormValues = {
  description?: string;
  name: string;
  permissionIds: string[];
};

type AssignmentScopeType = "global" | "project" | "secret" | "vault";

type UserRole = {
  actorId: string;
  assignedAt?: string;
  assignedBy?: string;
  id: string;
  roleId: string;
  roleName: string;
  scopeId?: string;
  scopeType: AssignmentScopeType;
  status: "active" | "revoked";
};

type UserRoleList = {
  actorId: string;
  items: UserRole[];
  permissions: RbacActionPermissions;
};

type RoleAssignmentValues = {
  actorId: string;
  roleId: string;
};

export type {
  AssignmentScopeType,
  Permission,
  PermissionSensitivity,
  RbacAction,
  RbacActionPermissions,
  Role,
  RoleAssignmentValues,
  RoleFilters,
  RoleFormValues,
  RoleKind,
  RoleList,
  RoleStatus,
  UserRole,
  UserRoleList,
};
