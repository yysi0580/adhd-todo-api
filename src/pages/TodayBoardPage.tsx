import { ActiveActionPanel } from "../components/actions/ActiveActionPanel";
import { BrainDumpComposer } from "../components/brainDump/BrainDumpComposer";
import { Badge } from "../components/common/Badge";
import { Card } from "../components/common/Card";
import { FeedbackPanel } from "../components/suggestions/FeedbackPanel";
import { SuggestionBoard } from "../components/suggestions/SuggestionBoard";
import { mockHistoryRows } from "../mockData";

const metrics = [
  ["Today suggestions", "5"],
  ["Active actions", "1"],
  ["Feedback signals", "8"],
  ["Mode", "No pressure"],
];

export function TodayBoardPage() {
  return (
    <div className="space-y-5">
      <div className="grid grid-cols-4 gap-4">
        {metrics.map(([label, value]) => (
          <Card key={label} className="p-4">
            <div className="text-[12px] font-semibold text-textMuted">{label}</div>
            <div className="mt-2 text-[24px] font-bold text-textPrimary">{value}</div>
          </Card>
        ))}
      </div>
      <BrainDumpComposer compact />
      <div className="grid grid-cols-3 gap-5">
        <SuggestionBoard />
        <ActiveActionPanel />
        <div className="space-y-5">
          <FeedbackPanel />
          <Card title="Review / Signals" meta="최근 흐름과 예정 모듈을 함께 봅니다.">
            <div className="mb-4 flex flex-wrap gap-2">
              {["do", "pass", "snooze", "smaller"].map((signal) => (
                <Badge key={signal} tone={signal === "do" ? "green" : "muted"}>
                  {signal}
                </Badge>
              ))}
            </div>
            <div className="space-y-2">
              {mockHistoryRows.slice(0, 3).map((row) => (
                <div key={row.join("-")} className="flex justify-between text-[12px]">
                  <span className="text-textSecondary">{row[0]}</span>
                  <span className="text-textMuted">{row[2]}</span>
                </div>
              ))}
            </div>
            <div className="mt-4 grid grid-cols-1 gap-2 text-[12px] text-textSecondary">
              <div className="bg-input p-2">AI fallback / ready</div>
              <div className="bg-input p-2">Routines / enabled</div>
              <div className="bg-input p-2">Calendar import / planned</div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
