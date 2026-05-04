import { FeedbackPanel } from "../components/suggestions/FeedbackPanel";
import { SuggestionCard } from "../components/suggestions/SuggestionCard";
import { Badge } from "../components/common/Badge";
import { Card } from "../components/common/Card";
import { mockBrainDump, mockSmallerSuggestions, mockSuggestions } from "../mockData";

export function SuggestionsPage() {
  return (
    <div className="grid grid-cols-[1fr_340px] gap-5">
      <div className="space-y-5">
        <Card title="Original Brain Dump" meta="원본 입력 요약">
          <p className="text-[14px] leading-7 text-textSecondary">{mockBrainDump}</p>
        </Card>
        <div className="flex items-center gap-2 rounded-card border border-border bg-surface p-3">
          {["all", "quiet", "gentle", "neutral", "5 candidates", "session #22"].map((item) => (
            <Badge key={item} tone={item === "quiet" ? "quiet" : "muted"}>
              {item}
            </Badge>
          ))}
        </div>
        <div className="grid grid-cols-3 gap-4">
          {mockSuggestions.map((suggestion) => (
            <SuggestionCard key={suggestion.id} suggestion={suggestion} />
          ))}
        </div>
      </div>
      <div className="space-y-5">
        <FeedbackPanel />
        <Card title="make_smaller result" meta="부담이 느껴지는 후보를 더 작은 시작 행동으로 봅니다.">
          <div className="space-y-3">
            {mockSmallerSuggestions.map((suggestion) => (
              <SuggestionCard key={suggestion.id} suggestion={suggestion} compact />
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
