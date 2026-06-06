// Это экран входа для риелтора.
// Простыми словами: человек вводит свой логин и пароль, а страница отправляет их на backend и открывает рабочую часть приложения.
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowRight, CopyCheck, Radar, Send } from "lucide-react";
import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, ApiError } from "../shared/api";
import { loginPhoto, logoImage } from "../shared/assets";
import type { User } from "../entities/types";

export function LoginPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");

  const mutation = useMutation({
    mutationFn: () => api.post<{ user: User }>("/api/auth/login", { login, password }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["me"] });
      navigate("/dashboard", { replace: true });
    }
  });

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    mutation.mutate();
  };

  const error = mutation.error instanceof ApiError ? mutation.error.message : null;

  return (
    <div className="login-page">
      <section className="login-hero">
        <div className="brand brand--large">
          <img className="brand-logo brand-logo--large" src={logoImage} alt="Тэона" />
          <div>
            <strong>Тэона</strong>
            <span>Умный поиск недвижимости</span>
          </div>
        </div>

        <h1>Рабочее пространство риелтора для подбора недвижимости.</h1>
        <p>
          Добавляйте клиентов, задавайте параметры поиска, отбирайте объекты в подборку и копируйте готовый текст для отправки.
        </p>

        <div className="benefits">
          <div><Radar size={18} /> Live-поиск по объектам</div>
          <div><CopyCheck size={18} /> Подборка под каждого клиента</div>
          <div><Send size={18} /> Готовый текст для отправки</div>
        </div>
      </section>

      <section className="login-visual" style={{ backgroundImage: `url(${loginPhoto})` }}>
        <form className="auth-card login-card" onSubmit={onSubmit}>
          <div>
            <h2>Вход в аккаунт</h2>
            <p>Введите логин и пароль сотрудника агентства.</p>
          </div>

          <label>
            <span>Логин</span>
            <input value={login} onChange={(event) => setLogin(event.target.value)} placeholder="Введите логин" />
          </label>

          <label>
            <span>Пароль</span>
            <input value={password} type="password" onChange={(event) => setPassword(event.target.value)} placeholder="Введите пароль" />
          </label>

          {error ? <div className="form-error">{error}</div> : null}

          <button className="button button--primary" disabled={mutation.isPending} type="submit">
            {mutation.isPending ? "Входим..." : "Войти"}
            <ArrowRight size={18} />
          </button>
        </form>
      </section>
    </div>
  );
}
