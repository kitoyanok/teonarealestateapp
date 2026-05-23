// Эта страница содержит базовые настройки и выход из системы.
// Проще говоря: здесь пользователь видит свои данные и может завершить работу с аккаунтом.

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { LogOut, Save } from "lucide-react";
import { useNavigate } from "react-router-dom";
import type { User } from "../entities/types";
import { api } from "../shared/api";

export function SettingsPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const me = useQuery({
    queryKey: ["me"],
    queryFn: () => api.get<{ user: User }>("/api/auth/me")
  });
  const logout = useMutation({
    mutationFn: () => api.post("/api/auth/logout"),
    onSuccess: async () => {
      await queryClient.clear();
      navigate("/login", { replace: true });
    }
  });

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Настройки</h1>
          <p>Минимальные настройки профиля и интерфейса.</p>
        </div>
      </header>

      <section className="settings-grid">
        <article className="panel form-section">
          <div className="form-section__header">
            <h2>Профиль риелтора</h2>
            <span>Данные аккаунта</span>
          </div>
          <div className="form-grid">
            <label>
              <span>Имя</span>
              <input defaultValue={me.data?.user.name ?? ""} />
            </label>
            <label>
              <span>Телефон</span>
              <input defaultValue={me.data?.user.phone ?? ""} />
            </label>
            <label className="span-2">
              <span>Email</span>
              <input defaultValue={me.data?.user.email ?? ""} />
            </label>
          </div>
          <button className="button button--primary" type="button"><Save size={18} /> Сохранить</button>
        </article>

        <article className="panel settings-side">
          <h2>Интерфейс</h2>
          <div className="settings-row"><span>Тема</span><strong>светлая</strong></div>
          <div className="settings-row"><span>Акцент</span><strong className="accent-text">оранжевый</strong></div>
          <h2>Сервис</h2>
          <div className="settings-row"><span>Режим поиска</span><strong>Live only</strong></div>
          <div className="settings-row"><span>Отправка</span><strong>копирование вручную</strong></div>
          <button className="button" type="button" onClick={() => logout.mutate()}><LogOut size={18} /> Выйти</button>
        </article>
      </section>
    </div>
  );
}
