import { ActiveActionPanel } from "../components/actions/ActiveActionPanel";
import { Button } from "../components/common/Button";
import { Card } from "../components/common/Card";
import { Input } from "../components/common/Input";
import { mockActiveAction, mockSmallerSuggestions } from "../mockData";

export function ActiveActionPage() {
  return (
    <div className="grid grid-cols-[1fr_360px] gap-5">
      <div className="space-y-5">
        <ActiveActionPanel />
        <Card title="Abort reason" meta="선택 사항입니다. 다음 제안 크기를 줄이는 내부 신호로만 저장됩니다.">
          <Input placeholder="지금은 너무 크게 느껴짐" />
          <Button className="mt-3" variant="secondary">
            save reason
          </Button>
        </Card>
        <Card title="Related smaller actions" meta="원한다면 더 작은 단위에서 다시 시작할 수 있습니다.">
          <div className="grid grid-cols-3 gap-3">
            {mockSmallerSuggestions.map((suggestion) => (
              <div key={suggestion.id} className="border border-border bg-input p-3">
                <div className="text-[13px] font-bold">{suggestion.title}</div>
                <p className="mt-1 text-[12px] leading-5 text-textSecondary">
                  {suggestion.micro_step}
                </p>
              </div>
            ))}
          </div>
        </Card>
      </div>
      <Card title="Action detail" meta="Action은 선택 이후 하나로 수렴합니다.">
        <div className="space-y-3 text-[13px] text-textSecondary">
          <Row label="status" value={mockActiveAction.status} />
          <Row label="session id" value={`#${mockActiveAction.session_id}`} />
          <Row label="suggestion id" value={`#${mockActiveAction.suggestion_id}`} />
          <Row label="estimated time" value="2-5 min" />
        </div>
        <div className="mt-5 space-y-2 border-l-2 border-primary pl-3 text-[12px] text-textSecondary">
          {["Brain Dump", "Suggestion selected", "Feedback do", "Action active", "Complete or Abort"].map(
            (step) => (
              <div key={step}>{step}</div>
            ),
          )}
        </div>
      </Card>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between border-b border-border pb-2">
      <span>{label}</span>
      <strong className="text-textPrimary">{value}</strong>
    </div>
  );
}
