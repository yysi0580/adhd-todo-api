import type { ButtonHTMLAttributes, ReactNode } from "react";

type ButtonVariant = "primary" | "secondary" | "ghost" | "quiet";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  icon?: ReactNode;
}

const variants: Record<ButtonVariant, string> = {
  primary: "border-primary bg-primary text-white hover:bg-[#1e4038]",
  secondary: "border-border bg-surface text-textPrimary hover:bg-surfaceSubtle",
  ghost: "border-transparent bg-transparent text-textSecondary hover:bg-surfaceSubtle",
  quiet: "border-primarySoft bg-primarySoft text-primary hover:bg-[#c8d9d0]",
};

export function Button({
  className = "",
  variant = "secondary",
  icon,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={`inline-flex h-9 items-center justify-center gap-2 rounded-sm border px-3 text-[13px] font-semibold transition ${variants[variant]} ${className}`}
      {...props}
    >
      {icon}
      {children}
    </button>
  );
}
