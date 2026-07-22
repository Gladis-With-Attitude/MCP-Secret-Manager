import type { QueryParams } from "@/lib/api";

type PermissionDto = {
  action?: string | null;
  description?: string | null;
  group?: string | null;
  id: string;
  name: string;
  resource?: string | null;
  sensitivity?: string | null;
};

type RbacPermissionDto = {
  assign?: boolean;
  create?: boolean;
  read?: boolean;
  revoke?: boolean;
  update?: boolean;
};

type RoleDto = {
  assignments_count?: number | null;
  created_at?: string | null;
  description?: string | null;
  id: string;
  is_system?: boolean | null;
  kind?: string | null;
  name: string;
  permission_ids?: string[] | null;
  permissions?: PermissionDto[] | null;
  permissions_count?: number | null;
  status?: string | null;
  updated_at?: string | null;
  ui_permissions?: RbacPermissionDto | null;
};

type RoleListResponseDto =
  | RoleDto[]
  | {
      data: RoleDto[];
      limit?: number;
      offset?: number;
      permissions?: RbacPermissionDto | null;
      total?: number;
    };

type PermissionListResponseDto =
  | PermissionDto[]
  | {
      data: PermissionDto[];
    };

type UserRoleDto = {
  actor_id?: string | null;
  assigned_at?: string | null;
  assigned_by?: string | null;
  id?: string | null;
  role?: RoleDto | null;
  role_id: string;
  role_name?: string | null;
  scope_id?: string | null;
  scope_type?: string | null;
  status?: string | null;
};

type UserRoleListResponseDto =
  | UserRoleDto[]
  | {
      actor_id?: string;
      data: UserRoleDto[];
      permissions?: RbacPermissionDto | null;
    };

type RoleListParamsDto = QueryParams & {
  kind?: string;
  limit?: number;
  offset?: number;
  q?: string;
  search?: string;
  status?: string;
};

type CreateRoleDto = {
  description?: string;
  name: string;
  permission_ids: string[];
};

type UpdateRoleDto = Partial<CreateRoleDto>;

export type {
  CreateRoleDto,
  PermissionDto,
  PermissionListResponseDto,
  RbacPermissionDto,
  RoleDto,
  RoleListParamsDto,
  RoleListResponseDto,
  UpdateRoleDto,
  UserRoleDto,
  UserRoleListResponseDto,
};
