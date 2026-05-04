import { Search } from "lucide-react";

import { Input } from "../common/Input";

interface TopbarProps {
  title: string;
  subtitle: string;
}

export function Topbar({ title, subtitle }: TopbarProps) {
  return (
    <header className="sticky top-0 z-20 border-b border-border bg-background/95 backdrop-blur">
      <div className="flex h-[84px] items-center justify-between gap-6 px-10">
        <div>
          <h1 className="text-[30px] font-bold tracking-[-0.01em] text-textPrimary">{title}</h1>
          <p className="mt-1 text-[13px] text-textSecondary">{subtitle}</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative w-[280px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-textMuted" size={16} />
            <Input className="pl-9" placeholder="Search session, action, signal" />
          </div>
          <div className="flex h-10 items-center gap-3 rounded-sm border border-border bg-surface px-3">
            <div className="h-6 w-6 rounded-sm bg-primarySoft" />
            <div>
              <div className="text-[12px] font-bold text-textPrimary">yangtheory</div>
              <div className="text-[11px] text-textMuted">protected session</div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
