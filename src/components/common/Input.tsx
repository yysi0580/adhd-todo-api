import type { InputHTMLAttributes } from "react";

export function Input({ className = "", ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={`h-10 w-full rounded-sm border border-border bg-input px-3 text-[14px] text-textPrimary outline-none transition placeholder:text-textMuted focus:border-primary ${className}`}
      {...props}
    />
  );
}
