type NavigationItemId =
  | "api-keys"
  | "audit"
  | "dashboard"
  | "profile"
  | "projects"
  | "rbac"
  | "secrets"
  | "settings"
  | "vaults";

type NavigationItem = {
  activePathPatterns?: string[];
  description: string;
  href: string;
  id: NavigationItemId;
  label: string;
};

type NavigationSection = {
  id: string;
  items: NavigationItem[];
  label: string;
};

const navigationSections: NavigationSection[] = [
  {
    id: "workspace",
    label: "Workspace",
    items: [
      {
        description: "Operational overview.",
        href: "/dashboard",
        id: "dashboard",
        label: "Dashboard",
      },
      {
        description: "Vault metadata and lifecycle.",
        href: "/vaults",
        id: "vaults",
        label: "Vaults",
      },
      {
        activePathPatterns: ["/vaults/*/projects", "/vaults/*/projects/*"],
        description: "Projects organized inside vaults.",
        href: "/projects",
        id: "projects",
        label: "Projects",
      },
      {
        activePathPatterns: ["/vaults/*/projects/*/secrets", "/vaults/*/projects/*/secrets/*"],
        description: "Secret metadata and sensitive value access.",
        href: "/secrets",
        id: "secrets",
        label: "Secrets",
      },
      {
        activePathPatterns: ["/api-keys", "/api-keys/*"],
        description: "API keys for agents and integrations.",
        href: "/api-keys",
        id: "api-keys",
        label: "API Keys",
      },
      {
        activePathPatterns: ["/audit", "/audit/*"],
        description: "Backend-generated security events.",
        href: "/audit",
        id: "audit",
        label: "Audit Logs",
      },
      {
        description: "Access control placeholder.",
        href: "/rbac",
        id: "rbac",
        label: "RBAC",
      },
    ],
  },
  {
    id: "account",
    label: "Account",
    items: [
      {
        description: "Profile placeholder.",
        href: "/profile",
        id: "profile",
        label: "Profile",
      },
      {
        description: "Settings placeholder.",
        href: "/settings",
        id: "settings",
        label: "Settings",
      },
    ],
  },
];

const navigationItems = navigationSections.flatMap((section) => section.items);

export { navigationItems, navigationSections };
export type { NavigationItem, NavigationItemId, NavigationSection };
