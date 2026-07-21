import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { Loader2 } from "lucide-react";
import type { ButtonHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:pointer-events-none disabled:opacity-50",
  {
    defaultVariants: {
      size: "default",
      variant: "primary",
    },
    variants: {
      fullWidth: {
        false: "",
        true: "w-full",
      },
      size: {
        compact: "h-8 px-3 text-xs",
        default: "h-10 px-4",
        lg: "h-11 px-5",
      },
      variant: {
        danger:
          "bg-destructive text-white shadow-sm hover:bg-destructive/90 dark:bg-destructive dark:text-white",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        outline:
          "border border-border bg-background shadow-sm hover:bg-accent hover:text-accent-foreground",
        primary: "bg-primary text-primary-foreground shadow-sm hover:bg-primary/90",
        secondary: "bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80",
      },
    },
  },
);

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean;
    isLoading?: boolean;
  };

function Button({
  asChild = false,
  children,
  className,
  disabled,
  fullWidth,
  isLoading = false,
  size,
  type = "button",
  variant,
  ...props
}: ButtonProps) {
  const Component = asChild ? Slot : "button";

  return (
    <Component
      aria-busy={isLoading || undefined}
      className={cn(buttonVariants({ fullWidth, size, variant }), className)}
      disabled={!asChild ? disabled || isLoading : undefined}
      type={!asChild ? type : undefined}
      {...props}
    >
      {isLoading ? <Loader2 aria-hidden="true" className="size-4 animate-spin" /> : null}
      {children}
    </Component>
  );
}

export { Button, buttonVariants };
export type { ButtonProps };
