import { mockFeedback } from "../../mockData";
import { Badge } from "../common/Badge";
import { Card } from "../common/Card";

export function HistoryTimeline() {
  return (
    <Card title="Signals" meta="반응 신호는 다음 제안 크기를 조절하는 기록입니다.">
      <div className="space-y-3">
        {mockFeedback.map((feedback) => (
          <div key={feedback.id} className="flex items-start justify-between border-b border-border pb-3">
            <div>
              <Badge tone={feedback.reaction === "do" ? "green" : "muted"}>
                {feedback.reaction}
              </Badge>
              <p className="mt-2 text-[13px] text-textSecondary">
                {feedback.note ?? "반응만 저장됨"}
              </p>
            </div>
            <span className="text-[11px] text-textMuted">{feedback.created_at}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}
