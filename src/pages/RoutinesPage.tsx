import { Card } from "../components/common/Card";
import { RoutineList } from "../components/routines/RoutineList";

export function RoutinesPage() {
  return (
    <div className="space-y-5">
      <Card title="Safety net routines" meta="제안이 막힐 때 사용할 부담 낮은 행동 풀입니다.">
        <p className="text-[13px] leading-6 text-textSecondary">
          Routine은 체크리스트가 아니라 제안이 끊겼을 때 돌아올 수 있는 안전망 후보입니다.
        </p>
      </Card>
      <RoutineList />
      <Card title="Routine pool settings" meta="fallback 후보 풀의 상태입니다.">
        <table className="w-full text-left text-[13px]">
          <tbody>
            {[
              ["quiet fallback", "enabled"],
              ["gentle fallback", "enabled"],
              ["calendar candidates", "planned"],
            ].map(([label, status]) => (
              <tr key={label} className="border-b border-border">
                <td className="py-3 text-textSecondary">{label}</td>
                <td className="py-3 font-bold text-textPrimary">{status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
