import { useQuery } from "@tanstack/react-query";
import type { User } from "../entities/types";
import { api } from "../shared/api";

export function ProfilePage() {
  const me = useQuery({
    queryKey: ["me"],
    queryFn: () => api.get<{ user: User }>("/api/auth/me")
  });

  return (
    <div className="page">
      <header className="page-header page-header--compact">
        <div>
          <h1>Профиль</h1>
          <p>Данные риелтора</p>
        </div>
      </header>

      <section className="panel form-section">
        <div className="form-section__header">
          <h2>Профиль</h2>
          <span>Базовые данные аккаунта</span>
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
          <label className="span-2">
            <span>Фото профиля</span>
            <input defaultValue="Загрузка фото будет доступна позже" disabled />
          </label>
        </div>
        <div className="form-actions">
          <button className="button button--primary" type="button">Сохранить</button>
        </div>
      </section>
    </div>
  );
}
