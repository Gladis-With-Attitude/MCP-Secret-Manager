import { cva, type VariantProps } from "class-variance-authority";
import { Loader2 } from "lucide-react";
import type { ButtonHTMLAttributes, ReactNode } from "react";

import { cn } from "@/lib/utils";

const iconButtonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:pointer-events-none disabled:opacity-50",
  {
    defaultVariants: {
      size: "default",
      variant: "default",
    },
    variants: {
      size: {
        compact: "size-8",
        default: "size-10",
      },
      variant: {
        danger:
          "bg-destructive text-white shadow-sm hover:bg-destructive/90 dark:bg-destructive dark:text-white",
        default: "bg-primary text-primary-foreground shadow-sm hover:bg-primary/90",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        outline:
          "border border-border bg-background shadow-sm hover:bg-accent hover:text-accent-foreground",
        table: "size-8 hover:bg-accent hover:text-accent-foreground",
        toolbar:
          "size-8 border border-transparent bg-transparent hover:border-border hover:bg-accent hover:text-accent-foreground",
      },
    },
  },
);

type IconButtonProps = Omit<ButtonHTMLAttributes<HTMLButtonElement>, "children"> &
  VariantProps<typeof iconButtonVariants> & {
    label: string;
    icon: ReactNode;
    isLoading?: boolean;
  };

function IconButton({
  className,
  disabled,
  icon,
  isLoading = false,
  label,
  size = "default",
  type = "button",
  variant = "ghost",
  ...props
}: IconButtonProps) {
  return (
    <button
      aria-busy={isLoading || undefined}
      aria-label={label}
      className={cn(iconButtonVariants({ size, variant }), className)}
      disabled={disabled || isLoading}
      title={label}
      type={type}
      {...props}
    >
      {isLoading ? (
        <Loader2 aria-hidden="true" className="size-4 animate-spin" />
      ) : (
        <span aria-hidden="true" className="flex size-4 items-center justify-center">
          {icon}
        </span>
      )}
    </button>
  );
}

export { IconButton, iconButtonVariants };
export type { IconButtonProps };
