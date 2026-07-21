"use client";

import { usePathname } from "next/navigation";

import { Breadcrumb } from "@/components/navigation/breadcrumb";
import { type BreadcrumbLabelMap, createBreadcrumbs } from "@/lib/navigation";

type BreadcrumbBarProps = {
  labels?: BreadcrumbLabelMap;
};

function BreadcrumbBar({ labels }: BreadcrumbBarProps) {
  const pathname = usePathname();

  return <Breadcrumb items={createBreadcrumbs(pathname, labels)} />;
}

export { BreadcrumbBar };
export type { BreadcrumbBarProps };
