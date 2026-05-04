import { Button } from "../common/Button";
import { Card } from "../common/Card";

export function CalendarImportPanel() {
  return (
    <Card title="Calendar Import" meta="캘린더 일정은 1회 흡수 후 후보로 전환하는 방식입니다.">
      <div className="rounded-card border border-dashed border-border bg-input p-4">
        <p className="text-[13px] leading-6 text-textSecondary">
          planned: calendar candidates를 Brain Dump처럼 흡수하고 micro-action 후보로 보여줍니다.
        </p>
        <Button className="mt-4" variant="quiet">
          import calendar snapshot
        </Button>
      </div>
    </Card>
  );
}
