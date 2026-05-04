import { ArrowRight, ShieldCheck } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";

import { Button } from "../components/common/Button";
import { Input } from "../components/common/Input";

export function LoginPage() {
  const navigate = useNavigate();

  return (
    <div className="grid min-h-screen grid-cols-[1.05fr_0.95fr] bg-background">
      <section className="flex flex-col justify-between bg-navy p-12 text-white">
        <div>
          <div className="text-[24px] font-bold">Decide</div>
          <div className="mt-1 text-[13px] text-white/60">ADHD Todo System</div>
        </div>
        <div>
          <h1 className="max-w-[520px] text-[42px] font-bold leading-[1.12] tracking-[-0.02em]">
            생각을 정리하지 않아도 작은 행동으로 시작할 수 있게
          </h1>
          <p className="mt-5 max-w-[560px] text-[15px] leading-7 text-white/70">
            할 일 목록을 직접 관리하게 만들지 않습니다. Brain Dump를 입력하면 시스템이 여러
            개의 micro-action 후보로 나누고, 사용자는 하나를 선택합니다.
          </p>
          <div className="mt-8 grid max-w-[620px] grid-cols-2 gap-3">
            <div className="border border-white/15 bg-white/5 p-4">
              <div className="mb-2 text-[12px] text-white/50">Brain Dump</div>
              <p className="text-[13px] leading-6 text-white/80">
                발표 준비해야 하는데 자료도 없고 메일도 보내야 하고...
              </p>
            </div>
            <div className="space-y-3">
              {["발표 자료 제목만 작성", "교수님 메일 첫 줄 쓰기"].map((item) => (
                <div key={item} className="border-l-2 border-primarySoft bg-white/5 p-3">
                  <div className="text-[12px] font-semibold text-white">{item}</div>
                  <p className="mt-1 text-[11px] text-white/55">quiet micro-action</p>
                </div>
              ))}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2 text-[12px] text-white/55">
          <ShieldCheck size={15} />
          No pressure mode. Signals are not failure labels.
        </div>
      </section>

      <section className="flex items-center justify-center p-12">
        <div className="w-[420px] rounded-panel border border-border bg-surface p-8 shadow-subtle">
          <h2 className="text-[26px] font-bold text-textPrimary">Login</h2>
          <p className="mt-2 text-[13px] leading-6 text-textSecondary">
            JWT access / refresh token, login protection, rate limiting이 적용됩니다.
          </p>
          <div className="mt-7 space-y-4">
            <Input placeholder="email" type="email" />
            <Input placeholder="password" type="password" />
            <Button className="w-full" variant="primary" onClick={() => navigate("/today")}>
              login
              <ArrowRight size={15} />
            </Button>
          </div>
          <div className="mt-5 text-[13px] text-textSecondary">
            계정이 없다면{" "}
            <Link className="font-bold text-primary" to="/register">
              register
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
