import type { ReactNode } from "react";

type BadgeTone = "quiet" | "gentle" | "neutral" | "active" | "muted" | "amber" | "green";

const tones: Record<BadgeTone, string> = {
  quiet: "border-primarySoft bg-primarySoft text-primary",
  gentle: "border-[#d9d4c8] bg-surfaceSubtle text-textSecondary",
  neutral: "border-[#d5dbea] bg-[#eef2f8] text-blue",
  active: "border-primary bg-primary text-white",
  muted: "border-border bg-input text-textSecondary",
  amber: "border-[#ead4b7] bg-[#f8efe3] text-amber",
  green: "border-[#c9ddcf] bg-[#e7f0ea] text-green",
};

interface BadgeProps {
  children: ReactNode;
  tone?: BadgeTone;
}

export function Badge({ children, tone = "muted" }: BadgeProps) {
  return (
    <span
      className={`inline-flex h-6 items-center rounded-sm border px-2 text-[11px] font-semibold ${tones[tone]}`}
    >
      {children}
    </span>
  );
}
