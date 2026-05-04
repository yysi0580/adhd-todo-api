import { Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "./components/layout/AppLayout";
import { ActiveActionPage } from "./pages/ActiveActionPage";
import { BrainDumpPage } from "./pages/BrainDumpPage";
import { HistoryPage } from "./pages/HistoryPage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { RoutinesPage } from "./pages/RoutinesPage";
import { SettingsPage } from "./pages/SettingsPage";
import { SuggestionsPage } from "./pages/SuggestionsPage";
import { TodayBoardPage } from "./pages/TodayBoardPage";

export function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/today" replace />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route element={<AppLayout />}>
        <Route path="/today" element={<TodayBoardPage />} />
        <Route path="/brain-dumps" element={<BrainDumpPage />} />
        <Route path="/suggestions" element={<SuggestionsPage />} />
        <Route path="/actions/active" element={<ActiveActionPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/routines" element={<RoutinesPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  );
}
