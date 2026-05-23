// Это внешний каркас защищенной части приложения.
// Проще говоря: здесь живут меню, верхняя панель, кнопки навигации и общая оболочка рабочих страниц.

import { useEffect, useMemo, useRef, useState, type FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  BarChart3,
  CircleHelp,
  Home,
  Search,
  Settings,
  User,
  UserPlus,
  Users,
  LogOut
} from "lucide-react";
import { Link, NavLink, Outlet, useLocation, useMatch, useNavigate } from "react-router-dom";
import { api } from "../shared/api";
import { logoImage } from "../shared/assets";
import type { Client, DashboardSummary, User as UserType } from "../entities/types";

const navItems = [
  { to: "/dashboard", label: "Главная", icon: Home },
  { to: "/clients", label: "Клиенты", icon: Users },
  { to: "/analytics", label: "Аналитика", icon: BarChart3 }
];

function useTopbarMeta() {
  const location = useLocation();
  const navigate = useNavigate();
  const clientMatch = useMatch("/clients/:id");
  const [searchValue, setSearchValue] = useState("");

  const clientQuery = useQuery({
    queryKey: ["shell-client", clientMatch?.params.id],
    queryFn: () => api.get<Client>(`/api/clients/${clientMatch?.params.id}`),
    enabled: Boolean(clientMatch?.params.id)
  });

  const breadcrumb = useMemo(() => {
    if (clientMatch) {
      return `Клиенты / ${clientQuery.data?.name ?? "Карточка клиента"}`;
    }
    if (location.pathname.startsWith("/clients/new")) return "Клиенты";
    if (location.pathname.startsWith("/clients")) return "Клиенты";
    if (location.pathname.startsWith("/analytics")) return "Аналитика";
    if (location.pathname.startsWith("/settings")) return "Настройки";
    if (location.pathname.startsWith("/profile")) return "Профиль";
    if (location.pathname.startsWith("/help")) return "Помощь";
    return "Главная";
  }, [clientMatch, clientQuery.data?.name, location.pathname]);

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    const query = searchValue.trim();
    navigate(`/clients${query ? `?search=${encodeURIComponent(query)}` : ""}`);
  };

  const topbarAction = clientMatch
    ? <a className="button button--primary" href="#share-shortlist">Отправить подборку</a>
    : <Link className="button button--primary" to="/clients/new"><UserPlus size={16} />Добавить клиента</Link>;

  return { breadcrumb, searchValue, setSearchValue, onSubmit, topbarAction };
}

export function AppShell() {
  const navigate = useNavigate();
  const location = useLocation();
  const queryClient = useQueryClient();
  const { breadcrumb, searchValue, setSearchValue, onSubmit, topbarAction } = useTopbarMeta();
  const popupRef = useRef<HTMLDivElement | null>(null);
  const avatarRef = useRef<HTMLButtonElement | null>(null);
  const [accountOpen, setAccountOpen] = useState(false);

  const me = useQuery({
    queryKey: ["me"],
    queryFn: () => api.get<{ user: UserType }>("/api/auth/me")
  });
  const dashboard = useQuery({
    queryKey: ["dashboard", "summary"],
    queryFn: () => api.get<DashboardSummary>("/api/dashboard/summary")
  });

  const logout = useMutation({
    mutationFn: () => api.post("/api/auth/logout"),
    onSuccess: async () => {
      await queryClient.clear();
      navigate("/login", { replace: true });
    }
  });

  useEffect(() => {
    if (!accountOpen) return;
    const onPointerDown = (event: MouseEvent) => {
      const target = event.target as Node;
      if (popupRef.current?.contains(target) || avatarRef.current?.contains(target)) return;
      setAccountOpen(false);
    };
    const onEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") setAccountOpen(false);
    };
    document.addEventListener("mousedown", onPointerDown);
    document.addEventListener("keydown", onEscape);
    return () => {
      document.removeEventListener("mousedown", onPointerDown);
      document.removeEventListener("keydown", onEscape);
    };
  }, [accountOpen]);

  useEffect(() => {
    setAccountOpen(false);
  }, [location.pathname]);

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar__brand">
          <img className="brand-logo" src={logoImage} alt="Тэона" />
          <div>
            <strong>Тэона</strong>
            <span>Умный поиск недвижимости</span>
          </div>
        </div>

        <nav className="sidebar__nav">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink key={item.to} to={item.to} className={({ isActive }) => `nav-item ${isActive ? "is-active" : ""}`}>
                <Icon size={16} />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        <div className="sidebar__footer">
          <div className="sidebar-note">
            <strong>Добрый вечер, {me.data?.user.name?.split(" ")[0] ?? "Риелтор"}.</strong>
            <p>
              Сегодня у вас <b>{dashboard.data?.clientsInWork ?? 0}</b> клиента в работе и{" "}
              <b>{dashboard.data?.readyToSend ?? 0}</b> подборки готовы к отправке.
            </p>
          </div>
        </div>
      </aside>

      <div className="app-main">
        <header className="topbar">
          <div className="topbar__crumb">{breadcrumb}</div>
          <form className="topbar-search" onSubmit={onSubmit}>
            <Search size={16} />
            <input value={searchValue} onChange={(event) => setSearchValue(event.target.value)} placeholder="Поиск по клиентам..." />
          </form>
          <div className="topbar__actions">
            {topbarAction}
            <div className="account-menu">
              <button
                ref={avatarRef}
                className="avatar avatar-button"
                type="button"
                onClick={() => setAccountOpen((value) => !value)}
                aria-expanded={accountOpen}
                aria-haspopup="menu"
              >
                {me.data?.user.name?.slice(0, 1).toUpperCase() ?? "Р"}
              </button>
              {accountOpen ? (
                <div ref={popupRef} className="account-popup" role="menu">
                  <div className="account-popup__head">
                    <div className="avatar avatar--large">{me.data?.user.name?.slice(0, 1).toUpperCase() ?? "Р"}</div>
                    <div>
                      <strong>{me.data?.user.name ?? "Риелтор"}</strong>
                      <span>{me.data?.user.email ?? "realtor@example.com"}</span>
                    </div>
                  </div>
                  <Link className="account-item" to="/profile"><User size={16} />Профиль</Link>
                  <Link className="account-item" to="/help"><CircleHelp size={16} />Помощь</Link>
                  <Link className="account-item" to="/settings"><Settings size={16} />Настройки</Link>
                  <button className="account-item account-item--danger" type="button" onClick={() => logout.mutate()}>
                    <LogOut size={16} />
                    Выйти
                  </button>
                </div>
              ) : null}
            </div>
          </div>
        </header>

        <main className="page-scroll">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
