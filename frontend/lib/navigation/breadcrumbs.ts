import { navigationItems } from "@/config/navigation";

type BreadcrumbRoute = {
  href?: string;
  label: string;
};

type BreadcrumbLabelMap = Record<string, string>;

const staticRouteLabels = new Map<string, string>([
  ["/", "Home"],
  ["new", "New"],
  ["edit", "Edit"],
  ...navigationItems.map((item) => [item.href, item.label] as const),
]);

function titleizeSegment(segment: string): string {
  return segment
    .split("-")
    .filter(Boolean)
    .map((part) => `${part.charAt(0).toUpperCase()}${part.slice(1)}`)
    .join(" ");
}

function createBreadcrumbs(
  pathname: string,
  dynamicLabels: BreadcrumbLabelMap = {},
): BreadcrumbRoute[] {
  const normalizedPath = pathname === "/" ? "/" : pathname.replace(/\/+$/, "");

  if (normalizedPath === "/") {
    return [{ label: staticRouteLabels.get("/") ?? "Home" }];
  }

  const segments = normalizedPath.split("/").filter(Boolean);
  const routes: BreadcrumbRoute[] = [{ href: "/", label: staticRouteLabels.get("/") ?? "Home" }];

  segments.forEach((segment, index) => {
    const href = `/${segments.slice(0, index + 1).join("/")}`;
    const isLast = index === segments.length - 1;
    const label =
      dynamicLabels[href] ??
      dynamicLabels[segment] ??
      staticRouteLabels.get(href) ??
      titleizeSegment(segment);

    routes.push({
      href: isLast ? undefined : href,
      label,
    });
  });

  return routes;
}

export { createBreadcrumbs, titleizeSegment };
export type { BreadcrumbLabelMap, BreadcrumbRoute };
