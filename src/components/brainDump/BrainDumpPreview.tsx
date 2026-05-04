import { mockSuggestions } from "../../mockData";
import { Badge } from "../common/Badge";
import { Card } from "../common/Card";

export function BrainDumpPreview() {
  return (
    <Card title="Generated preview" meta="생성 결과는 후보 카드로 먼저 확인합니다.">
      <div className="space-y-3">
        {mockSuggestions.slice(0, 3).map((suggestion) => (
          <div key={suggestion.id} className="border-l-2 border-primary bg-input p-3">
            <div className="mb-2 flex items-center gap-2">
              <Badge tone={suggestion.effort_level === "neutral" ? "neutral" : "quiet"}>
                {suggestion.effort_level}
              </Badge>
              <span className="text-[11px] text-textMuted">{suggestion.source}</span>
            </div>
            <div className="text-[13px] font-bold text-textPrimary">{suggestion.title}</div>
            <p className="mt-1 text-[12px] leading-5 text-textSecondary">
              {suggestion.micro_step}
            </p>
          </div>
        ))}
      </div>
    </Card>
  );
}
