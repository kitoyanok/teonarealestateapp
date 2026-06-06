// Эта страница содержит базовые настройки и выход из системы.
// Проще говоря: здесь пользователь редактирует свои данные и может завершить работу с аккаунтом.

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { LogOut, Save } from "lucide-react";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { z } from "zod";
import type { User } from "../entities/types";
import { api } from "../shared/api";
import { formatPhoneInput, isValidPhone, phoneErrorText } from "../shared/phone";

const settingsSchema = z.object({
  name: z.string().trim().min(2, "Укажите имя риелтора"),
  phone: z.string().min(1, phoneErrorText()).refine((value) => isValidPhone(value), phoneErrorText()),
  email: z.string().trim().email("Укажите корректный email").optional().or(z.literal(""))
});

type SettingsForm = z.infer<typeof settingsSchema>;

export function SettingsPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const me = useQuery({
    queryKey: ["me"],
    queryFn: () => api.get<{ user: User }>("/api/auth/me")
  });

  const form = useForm<SettingsForm>({
    resolver: zodResolver(settingsSchema),
    defaultValues: {
      name: "",
      phone: "",
      email: ""
    }
  });

  useEffect(() => {
    if (!me.data?.user) {
      return;
    }
    form.reset({
      name: me.data.user.name ?? "",
      phone: me.data.user.phone ? formatPhoneInput(me.data.user.phone) : "",
      email: me.data.user.email ?? ""
    });
  }, [form, me.data?.user]);

  const saveProfile = useMutation({
    mutationFn: (values: SettingsForm) => api.put<{ user: User }>("/api/auth/me", values),
    onSuccess: async ({ user }) => {
      queryClient.setQueryData(["me"], { user });
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["me"] }),
        queryClient.invalidateQueries({ queryKey: ["clients"] }),
        queryClient.invalidateQueries({ queryKey: ["dashboard"] })
      ]);
    }
  });

  const logout = useMutation({
    mutationFn: () => api.post("/api/auth/logout"),
    onSuccess: async () => {
      await queryClient.clear();
      navigate("/login", { replace: true });
    }
  });

  const phoneValue = form.watch("phone");

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
          <form className="form-grid" onSubmit={form.handleSubmit((values) => saveProfile.mutate(values))}>
            <label>
              <span>Имя</span>
              <input {...form.register("name")} />
              {form.formState.errors.name ? <small>{form.formState.errors.name.message}</small> : null}
            </label>
            <label>
              <span>Телефон</span>
              <input
                {...form.register("phone")}
                value={phoneValue || ""}
                onChange={(event) => form.setValue("phone", formatPhoneInput(event.target.value), { shouldValidate: true })}
                placeholder="+7 (999) 123-45-67"
              />
              {form.formState.errors.phone ? <small>{form.formState.errors.phone.message}</small> : null}
            </label>
            <label className="span-2">
              <span>Email</span>
              <input {...form.register("email")} placeholder="realtor@example.com" />
              {form.formState.errors.email ? <small>{form.formState.errors.email.message}</small> : null}
            </label>
            {saveProfile.error ? <div className="form-error span-2">{saveProfile.error.message}</div> : null}
            <button className="button button--primary" disabled={saveProfile.isPending} type="submit">
              <Save size={18} />
              {saveProfile.isPending ? "Сохраняем..." : "Сохранить"}
            </button>
          </form>
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
