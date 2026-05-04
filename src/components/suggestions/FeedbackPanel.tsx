import { Badge } from "../common/Badge";
import { Button } from "../common/Button";
import { Card } from "../common/Card";

const reactions = ["do", "snooze", "pass", "capture", "make_smaller"];

export function FeedbackPanel() {
  return (
    <Card
      title="Feedback reaction"
      meta="반응은 평가가 아니라 다음 제안을 조절하는 신호입니다."
    >
      <div className="flex flex-wrap gap-2">
        {reactions.map((reaction) => (
          <Badge key={reaction} tone={reaction === "do" ? "green" : "muted"}>
            {reaction}
          </Badge>
        ))}
      </div>
      <div className="mt-4 flex gap-2">
        <Button variant="secondary">기록만</Button>
        <Button variant="quiet">세션 종료</Button>
      </div>
    </Card>
  );
}
