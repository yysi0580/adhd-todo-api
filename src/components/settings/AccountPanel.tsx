import { Button } from "../common/Button";
import { Card } from "../common/Card";

export function AccountPanel() {
  return (
    <Card title="Account / Security" meta="JWT access / refresh token과 login protection 상태입니다.">
      <div className="space-y-3 text-[13px] text-textSecondary">
        <div className="flex justify-between border-b border-border pb-2">
          <span>user email</span>
          <strong className="text-textPrimary">yangtheory@example.com</strong>
        </div>
        <div className="flex justify-between border-b border-border pb-2">
          <span>token flow</span>
          <strong className="text-textPrimary">access + refresh</strong>
        </div>
        <div className="flex justify-between border-b border-border pb-2">
          <span>login protection</span>
          <strong className="text-textPrimary">5 failures / 5 min block</strong>
        </div>
        <div className="flex justify-between border-b border-border pb-2">
          <span>rate limit</span>
          <strong className="text-textPrimary">login + brain dumps</strong>
        </div>
      </div>
      <Button className="mt-4" variant="secondary">
        logout
      </Button>
    </Card>
  );
}
