import { Archive, WandSparkles } from "lucide-react";

import { Button } from "../common/Button";
import { Card } from "../common/Card";
import { Textarea } from "../common/Textarea";

interface BrainDumpComposerProps {
  compact?: boolean;
}

export function BrainDumpComposer({ compact = false }: BrainDumpComposerProps) {
  return (
    <Card
      title={compact ? "Brain Dump" : "New Brain Dump"}
      meta={
        compact
          ? "정리하지 않은 문장 그대로 입력하세요. 시스템이 2~5개의 micro-action으로 분해합니다."
          : "생각을 정리하지 마세요. 여러 문장, 줄바꿈, 덩어리 입력 모두 허용합니다."
      }
    >
      <Textarea
        rows={compact ? 5 : 10}
        placeholder="예: 발표 준비해야 하는데 자료도 정리해야 하고 교수님께 질문 메일도 보내야 하고..."
      />
      <div className="mt-3 flex items-center justify-between">
        <p className="text-[12px] text-textMuted">쉼표, 줄바꿈, 긴 문장 모두 그대로 두세요.</p>
        <div className="flex gap-2">
          <Button variant="secondary" icon={<Archive size={15} />}>
            기록만
          </Button>
          <Button variant="primary" icon={<WandSparkles size={15} />}>
            후보 생성
          </Button>
        </div>
      </div>
    </Card>
  );
}
