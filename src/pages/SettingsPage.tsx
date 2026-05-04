import { AccountPanel } from "../components/settings/AccountPanel";
import { AiSettingsPanel } from "../components/settings/AiSettingsPanel";
import { CalendarImportPanel } from "../components/settings/CalendarImportPanel";
import { Card } from "../components/common/Card";

const coverage = [
  "Auth register/login/refresh/users-me",
  "Brain Dump create + suggestions",
  "Suggestion list + make smaller",
  "Feedback do/pass/snooze/make_smaller/capture_only",
  "Action create/complete/abort",
  "History",
  "Routines",
  "Calendar Import",
];

export function SettingsPage() {
  return (
    <div className="grid grid-cols-2 gap-5">
      <AiSettingsPanel />
      <AccountPanel />
      <CalendarImportPanel />
      <Card title="API coverage" meta="프론트엔드가 담아야 할 백엔드 흐름입니다.">
        <div className="grid grid-cols-1 gap-2">
          {coverage.map((item) => (
            <div key={item} className="border border-border bg-input px-3 py-2 text-[13px]">
              {item}
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
