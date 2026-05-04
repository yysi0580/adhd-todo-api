import { Card } from "../components/common/Card";
import { HistoryTable } from "../components/history/HistoryTable";
import { HistoryTimeline } from "../components/history/HistoryTimeline";

export function HistoryPage() {
  return (
    <div className="grid grid-cols-[1fr_340px] gap-5">
      <HistoryTable />
      <div className="space-y-5">
        <Card title="Weekly summary" meta="성공률 대신 돌아온 흐름을 봅니다.">
          <div className="grid grid-cols-2 gap-3">
            {[
              ["Brain Dumps", "12"],
              ["Actions returned", "7"],
              ["Smaller requests", "5"],
              ["Capture only", "4"],
            ].map(([label, value]) => (
              <div key={label} className="bg-input p-3">
                <div className="text-[11px] text-textMuted">{label}</div>
                <div className="mt-1 text-[20px] font-bold">{value}</div>
              </div>
            ))}
          </div>
        </Card>
        <HistoryTimeline />
      </div>
    </div>
  );
}
