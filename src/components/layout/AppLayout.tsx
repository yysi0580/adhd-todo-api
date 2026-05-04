import { Outlet, useLocation } from "react-router-dom";

import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

const pageMeta: Record<string, { title: string; subtitle: string }> = {
  "/today": {
    title: "Today Board",
    subtitle: "Brain Dump에서 작은 후보를 만들고 하나의 Action으로 수렴합니다.",
  },
  "/brain-dumps": {
    title: "Brain Dumps",
    subtitle: "정리하지 않은 문장을 그대로 입력하고 후보 생성을 확인합니다.",
  },
  "/suggestions": {
    title: "Suggestions",
    subtitle: "후보를 비교하고 반응 신호를 남깁니다.",
  },
  "/actions/active": {
    title: "Active Action",
    subtitle: "선택된 하나의 행동만 차분하게 보여줍니다.",
  },
  "/history": {
    title: "History",
    subtitle: "성공률이 아니라 최근 흐름과 반응 신호를 확인합니다.",
  },
  "/routines": {
    title: "Routines",
    subtitle: "제안이 막힐 때 사용할 안전망 행동 풀입니다.",
  },
  "/settings": {
    title: "Settings",
    subtitle: "AI fallback, 계정, 보안, 캘린더 가져오기를 관리합니다.",
  },
};

export function AppLayout() {
  const location = useLocation();
  const meta = pageMeta[location.pathname] ?? pageMeta["/today"];

  return (
    <div className="min-h-screen bg-background">
      <Sidebar />
      <div className="ml-[244px] min-h-screen">
        <Topbar title={meta.title} subtitle={meta.subtitle} />
        <main className="px-10 py-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
