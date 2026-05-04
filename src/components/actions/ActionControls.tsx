import { Check, PauseCircle, Split } from "lucide-react";

import { Button } from "../common/Button";

export function ActionControls() {
  return (
    <div className="flex flex-wrap gap-2">
      <Button variant="primary" icon={<Check size={15} />}>
        완료
      </Button>
      <Button variant="secondary" icon={<PauseCircle size={15} />}>
        중단
      </Button>
      <Button variant="quiet" icon={<Split size={15} />}>
        더 작게 보기
      </Button>
    </div>
  );
}
