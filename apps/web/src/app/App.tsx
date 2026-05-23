// Это корневой файл frontend.
// Проще говоря: он задает маршруты приложения, проверяет авторизацию и решает, какую страницу показывать пользователю.

import { QueryClient, QueryClientProvider, useQuery } from "@tanstack/react-query";
import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";
import { AppShell } from "../widgets/AppShell";
import { api } from "../shared/api";
import type { User } from "../entities/types";
import { LoginPage } from "../pages/LoginPage";
import { DashboardPage } from "../pages/DashboardPage";
import { ClientsPage } from "../pages/ClientsPage";
import { NewClientPage } from "../pages/NewClientPage";
import { ClientPage } from "../pages/ClientPage";
import { SettingsPage } from "../pages/SettingsPage";
import { AnalyticsPage } from "../pages/AnalyticsPage";
import { ProfilePage } from "../pages/ProfilePage";
import { HelpPage } from "../pages/HelpPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 20_000
    }
  }
});

function useMe() {
  return useQuery({
    queryKey: ["me"],
    queryFn: () => api.get<{ user: User }>("/api/auth/me")
  });
}

function ProtectedRoutes() {
  const location = useLocation();
  const { data, isLoading } = useMe();

  if (isLoading) {
    return <div className="boot-screen">Загружаем EstateFlow...</div>;
  }

  if (!data?.user) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <AppShell />;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoutes />}>
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/clients" element={<ClientsPage />} />
        <Route path="/clients/new" element={<NewClientPage />} />
        <Route path="/clients/:id" element={<ClientPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/help" element={<HelpPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </QueryClientProvider>
  );
}
