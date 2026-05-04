import type { Routine } from "../../api/routines";
import { Badge } from "../common/Badge";
import { Button } from "../common/Button";

export function RoutineCard({ routine }: { routine: Routine }) {
  return (
    <article className="rounded-card border border-border bg-surface p-4 shadow-subtle">
      <div className="flex items-center justify-between">
        <Badge tone={routine.mode === "neutral" ? "neutral" : "quiet"}>{routine.mode}</Badge>
        <span className="text-[11px] text-textMuted">{routine.enabled ? "enabled" : "paused"}</span>
      </div>
      <h3 className="mt-3 text-[15px] font-bold text-textPrimary">{routine.title}</h3>
      <p className="mt-2 text-[13px] leading-6 text-textSecondary">{routine.micro_step}</p>
      <Button className="mt-4 w-full" variant={routine.enabled ? "secondary" : "primary"}>
        {routine.enabled ? "deactivate" : "activate"}
      </Button>
    </article>
  );
}
