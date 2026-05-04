import { BrainDumpComposer } from "../components/brainDump/BrainDumpComposer";
import { BrainDumpPreview } from "../components/brainDump/BrainDumpPreview";
import { Card } from "../components/common/Card";

const rows = [
  ["today 14:20", "프로젝트 발표 준비...", "5", "1"],
  ["yesterday", "메일과 일정 공유...", "3", "0"],
  ["monday", "책상 정리와 자료 찾기...", "2", "1"],
];

export function BrainDumpPage() {
  return (
    <div className="grid grid-cols-[1fr_360px] gap-5">
      <div className="space-y-5">
        <BrainDumpComposer />
        <Card title="Past brain dumps" meta="이전 입력과 생성된 후보 흐름입니다.">
          <table className="w-full text-left text-[13px]">
            <thead className="text-[12px] text-textMuted">
              <tr>
                <th className="pb-3">time</th>
                <th className="pb-3">summary</th>
                <th className="pb-3">candidates</th>
                <th className="pb-3">actions</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.join("-")} className="border-t border-border">
                  {row.map((cell) => (
                    <td key={cell} className="py-3 text-textSecondary">
                      {cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      </div>
      <BrainDumpPreview />
    </div>
  );
}
