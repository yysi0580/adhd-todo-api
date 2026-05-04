import { Link, useNavigate } from "react-router-dom";

import { Button } from "../components/common/Button";
import { Input } from "../components/common/Input";

export function RegisterPage() {
  const navigate = useNavigate();

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="w-[460px] rounded-panel border border-border bg-surface p-8 shadow-subtle">
        <div className="text-[24px] font-bold text-textPrimary">Create account</div>
        <p className="mt-2 text-[13px] leading-6 text-textSecondary">
          비밀번호는 8자 이상, 문자와 숫자를 포함해야 합니다.
        </p>
        <div className="mt-6 space-y-4">
          <Input placeholder="email" type="email" />
          <Input placeholder="password" type="password" />
          <Input placeholder="confirm password" type="password" />
          <Button className="w-full" variant="primary" onClick={() => navigate("/today")}>
            register
          </Button>
        </div>
        <div className="mt-5 text-[13px] text-textSecondary">
          이미 계정이 있다면{" "}
          <Link className="font-bold text-primary" to="/login">
            login
          </Link>
        </div>
      </div>
    </div>
  );
}
