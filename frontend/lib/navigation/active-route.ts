function matchPathPattern(pathname: string, pattern: string): boolean {
  const patternSegments = pattern.split("/").filter(Boolean);
  const pathSegments = pathname.split("/").filter(Boolean);

  if (pathSegments.length < patternSegments.length) {
    return false;
  }

  return patternSegments.every((segment, index) => {
    return segment === "*" || segment === pathSegments[index];
  });
}

function isActiveRoute(pathname: string, href: string, activePathPatterns: string[] = []): boolean {
  if (href === "/") {
    return pathname === "/";
  }

  return (
    pathname === href ||
    pathname.startsWith(`${href}/`) ||
    activePathPatterns.some((pattern) => matchPathPattern(pathname, pattern))
  );
}

export { isActiveRoute, matchPathPattern };
