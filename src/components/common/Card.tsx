import type { HTMLAttributes, ReactNode } from "react";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  title?: string;
  meta?: string;
  action?: ReactNode;
}

export function Card({ title, meta, action, children, className = "", ...props }: CardProps) {
  return (
    <section
      className={`rounded-card border border-border bg-surface shadow-subtle ${className}`}
      {...props}
    >
      {(title || meta || action) && (
        <div className="flex items-start justify-between gap-4 border-b border-border px-4 py-3">
          <div>
            {title && <h2 className="text-[15px] font-bold text-textPrimary">{title}</h2>}
            {meta && <p className="mt-1 text-[12px] leading-5 text-textSecondary">{meta}</p>}
          </div>
          {action}
        </div>
      )}
      <div className="p-4">{children}</div>
    </section>
  );
}
