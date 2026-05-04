import { mockActiveAction } from "../../mockData";
import { Badge } from "../common/Badge";
import { Card } from "../common/Card";
import { ActionControls } from "./ActionControls";

export function ActiveActionPanel() {
  return (
    <Card title="Active Action" meta="선택된 suggestion이 하나의 실행 단위로 수렴했습니다.">
      <Badge tone="active">active</Badge>
      <h2 className="mt-4 text-[20px] font-bold text-textPrimary">{mockActiveAction.title}</h2>
      <p className="mt-2 text-[14px] leading-6 text-textSecondary">{mockActiveAction.micro_step}</p>
      <div className="mt-4 rounded-card border border-border bg-input p-3 text-[12px] leading-5 text-textSecondary">
        중단해도 실패가 아닙니다. abort reason은 다음 제안 크기를 줄이는 내부 신호로만
        저장됩니다.
      </div>
      <div className="mt-4">
        <ActionControls />
      </div>
    </Card>
  );
}
