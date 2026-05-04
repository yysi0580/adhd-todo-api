import { mockSuggestions } from "../../mockData";
import { Card } from "../common/Card";
import { SuggestionCard } from "./SuggestionCard";

export function SuggestionBoard() {
  return (
    <Card title="Generated Suggestions" meta="처음부터 하나만 고르지 않고 후보를 비교합니다.">
      <div className="space-y-3">
        {mockSuggestions.map((suggestion) => (
          <SuggestionCard key={suggestion.id} suggestion={suggestion} />
        ))}
      </div>
    </Card>
  );
}
