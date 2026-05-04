import {
  Bot,
  CalendarDays,
  CheckSquare,
  ClipboardList,
  History,
  ListChecks,
  Settings,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { NavLink } from "react-router-dom";

const groups = [
  {
    label: "MAIN",
    items: [
      { to: "/today", label: "Today Board", icon: ClipboardList },
      { to: "/brain-dumps", label: "Brain Dumps", icon: ListChecks },
      { to: "/suggestions", label: "Suggestions", icon: Sparkles },
      { to: "/actions/active", label: "Actions", icon: CheckSquare },
    ],
  },
  {
    label: "REVIEW",
    items: [
      { to: "/history", label: "History", icon: History },
      { to: "/routines", label: "Routines", icon: ShieldCheck },
      { to: "/settings", label: "Calendar Import", icon: CalendarDays },
    ],
  },
  {
    label: "SYSTEM",
    items: [{ to: "/settings", label: "AI Settings / Account", icon: Bot }],
  },
];

export function Sidebar() {
  return (
    <aside className="fixed inset-y-0 left-0 flex w-[244px] flex-col border-r border-border bg-sidebar">
      <div className="border-b border-border px-5 py-5">
        <div className="text-[19px] font-bold tracking-tight text-textPrimary">Decide</div>
        <div className="mt-1 text-[12px] font-medium text-textSecondary">ADHD Todo System</div>
      </div>
      <nav className="flex-1 overflow-y-auto px-3 py-4">
        {groups.map((group) => (
          <div key={group.label} className="mb-6">
            <div className="mb-2 px-2 text-[11px] font-bold tracking-[0.08em] text-textMuted">
              {group.label}
            </div>
            <div className="space-y-1">
              {group.items.map((item) => (
                <NavLink
                  key={`${group.label}-${item.label}`}
                  to={item.to}
                  className={({ isActive }) =>
                    `flex h-9 items-center gap-2 rounded-sm px-2 text-[13px] font-medium transition ${
                      isActive
                        ? "bg-primarySoft text-primary"
                        : "text-textSecondary hover:bg-surfaceSubtle hover:text-textPrimary"
                    }`
                  }
                >
                  <item.icon size={16} />
                  {item.label}
                </NavLink>
              ))}
            </div>
          </div>
        ))}
      </nav>
      <div className="border-t border-border p-4">
        <div className="rounded-card border border-border bg-surface p-3">
          <div className="flex items-center gap-2 text-[12px] font-bold text-primary">
            <Settings size={14} />
            No pressure mode
          </div>
          <p className="mt-2 text-[12px] leading-5 text-textSecondary">
            반응은 실패가 아니라 다음 제안 조절 신호입니다.
          </p>
        </div>
      </div>
    </aside>
  );
}
