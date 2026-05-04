import { mockHistoryRows } from "../../mockData";
import { Card } from "../common/Card";

export function HistoryTable() {
  return (
    <Card title="Recent activity" meta="성공률이 아니라 최근 흐름을 확인합니다.">
      <table className="w-full border-collapse text-left">
        <thead>
          <tr className="border-b border-border text-[12px] text-textMuted">
            <th className="pb-3 font-bold">type</th>
            <th className="pb-3 font-bold">content</th>
            <th className="pb-3 font-bold">time</th>
            <th className="pb-3 font-bold">result</th>
          </tr>
        </thead>
        <tbody>
          {mockHistoryRows.map((row) => (
            <tr key={row.join("-")} className="border-b border-border text-[13px]">
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
  );
}
