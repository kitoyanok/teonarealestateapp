import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { ArrowLeft, Check, Loader2 } from "lucide-react";
import { useMemo } from "react";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import { z } from "zod";
import type { Client, PropertyType } from "../entities/types";
import { api } from "../shared/api";
import { formatPhoneInput, isValidPhone, normalizePhone, phoneErrorText } from "../shared/phone";

const formSchema = z.object({
  name: z.string().min(2, "Укажите имя клиента"),
  phone: z.string().min(1, phoneErrorText()).refine((value) => isValidPhone(value), phoneErrorText()),
  propertyType: z.enum(["apartment", "house"]),
  budgetMin: z.string().optional(),
  budgetMax: z.string().optional(),
  roomsMin: z.string().optional(),
  roomsMax: z.string().optional(),
  areaMin: z.string().optional(),
  areaMax: z.string().optional(),
  districts: z.string().optional(),
  completionYearMax: z.string().optional(),
  finishing: z.string().optional(),
  floorMin: z.string().optional(),
  floorMax: z.string().optional(),
  houseAreaMin: z.string().optional(),
  houseAreaMax: z.string().optional(),
  landAreaMin: z.string().optional(),
  landAreaMax: z.string().optional(),
  settlementNames: z.string().optional(),
  floorsCountMin: z.string().optional(),
  floorsCountMax: z.string().optional(),
  bedroomsMin: z.string().optional(),
  bedroomsMax: z.string().optional(),
  houseMaterial: z.string().optional(),
  communications: z.array(z.string()).default([]),
  comment: z.string().optional()
});

type ClientForm = z.infer<typeof formSchema>;

const numberOrUndefined = (value?: string) => {
  if (!value) {
    return undefined;
  }
  const number = Number(value);
  return Number.isFinite(number) ? number : undefined;
};

const toList = (value?: string) => value?.split(",").map((item) => item.trim()).filter(Boolean) ?? [];

function buildPayload(values: ClientForm) {
  return {
    name: values.name,
    phone: normalizePhone(values.phone) ?? values.phone,
    sendChannel: "copy",
    sendContact: normalizePhone(values.phone) ?? values.phone,
    propertyType: values.propertyType,
    comment: values.comment,
    searchProfile: {
      budgetMin: numberOrUndefined(values.budgetMin),
      budgetMax: numberOrUndefined(values.budgetMax),
      roomsMin: numberOrUndefined(values.roomsMin),
      roomsMax: numberOrUndefined(values.roomsMax),
      areaMin: numberOrUndefined(values.areaMin),
      areaMax: numberOrUndefined(values.areaMax),
      districts: toList(values.districts),
      settlementNames: toList(values.settlementNames),
      completionYearMax: numberOrUndefined(values.completionYearMax),
      finishing: values.finishing,
      floorMin: numberOrUndefined(values.floorMin),
      floorMax: numberOrUndefined(values.floorMax),
      houseAreaMin: numberOrUndefined(values.houseAreaMin),
      houseAreaMax: numberOrUndefined(values.houseAreaMax),
      landAreaMin: numberOrUndefined(values.landAreaMin),
      landAreaMax: numberOrUndefined(values.landAreaMax),
      floorsCountMin: numberOrUndefined(values.floorsCountMin),
      floorsCountMax: numberOrUndefined(values.floorsCountMax),
      bedroomsMin: numberOrUndefined(values.bedroomsMin),
      bedroomsMax: numberOrUndefined(values.bedroomsMax),
      houseMaterial: values.houseMaterial,
      communications: values.communications
    }
  };
}

export function NewClientPage() {
  const navigate = useNavigate();
  const form = useForm<ClientForm>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      propertyType: "apartment",
      communications: []
    }
  });
  const propertyType = form.watch("propertyType");
  const isHouse = propertyType === "house";
  const phoneValue = form.watch("phone");
  const budgetMin = form.watch("budgetMin");
  const budgetMax = form.watch("budgetMax");
  const roomsMin = form.watch("roomsMin");
  const areaMin = form.watch("areaMin");
  const houseAreaMin = form.watch("houseAreaMin");
  const landAreaMin = form.watch("landAreaMin");

  const createClient = useMutation({
    mutationFn: (values: ClientForm) => api.post<{ client: Client }>("/api/clients", buildPayload(values)),
    onSuccess: ({ client }) => navigate(`/clients/${client.id}`)
  });

  const communicationOptions = useMemo(() => ["Газ", "Электричество", "Вода", "Канализация", "Интернет"], []);
  const submitDisabled =
    createClient.isPending ||
    !form.watch("name")?.trim() ||
    !isValidPhone(phoneValue || "") ||
    !propertyType ||
    (!budgetMin?.trim() && !budgetMax?.trim()) ||
    (!isHouse && (!roomsMin?.trim() || !areaMin?.trim())) ||
    (isHouse && (!houseAreaMin?.trim() || !landAreaMin?.trim()));

  return (
    <div className="page">
      <header className="page-header page-header--compact">
        <div>
          <Link className="back-link" to="/clients"><ArrowLeft size={16} /> Клиенты</Link>
          <h1>Новый клиент</h1>
          <p>Заполните контакт и параметры поиска. После сохранения система сразу подберет подходящие варианты.</p>
        </div>
      </header>

      <form className="client-form" onSubmit={form.handleSubmit((values) => createClient.mutate(values))}>
        <section className="panel form-section">
          <div className="form-section__header">
            <h2>Контакт</h2>
            <span>Телефон понадобится для копирования подборки</span>
          </div>
          <div className="form-grid">
            <label>
              <span>Имя клиента</span>
              <input {...form.register("name")} placeholder="Иван Петров" />
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
          </div>
        </section>

        <section className="panel form-section">
          <div className="form-section__header">
            <h2>Тип недвижимости</h2>
            <span>Обязательный выбор для поиска</span>
          </div>
          <div className="segmented">
            {(["apartment", "house"] as PropertyType[]).map((type) => (
              <button
                className={propertyType === type ? "is-active" : ""}
                key={type}
                type="button"
                onClick={() => form.setValue("propertyType", type)}
              >
                {type === "apartment" ? "Квартира" : "Дом"}
              </button>
            ))}
          </div>

          <div className="form-grid">
            <label>
              <span>Бюджет от</span>
              <input {...form.register("budgetMin")} inputMode="numeric" placeholder="5000000" />
            </label>
            <label>
              <span>Бюджет до</span>
              <input {...form.register("budgetMax")} inputMode="numeric" placeholder="7000000" />
            </label>

            {!isHouse ? (
              <>
                <label>
                  <span>Комнатность от</span>
                  <select {...form.register("roomsMin")}>
                    <option value="">Не важно</option>
                    <option value="0">Студия</option>
                    <option value="1">1 комната</option>
                    <option value="2">2 комнаты</option>
                    <option value="3">3 комнаты</option>
                    <option value="4">4 комнаты</option>
                  </select>
                </label>
                <label>
                  <span>Комнатность до</span>
                  <select {...form.register("roomsMax")}>
                    <option value="">Не важно</option>
                    <option value="1">1 комната</option>
                    <option value="2">2 комнаты</option>
                    <option value="3">3 комнаты</option>
                    <option value="4">4 комнаты</option>
                  </select>
                </label>
                <label>
                  <span>Площадь от</span>
                  <input {...form.register("areaMin")} inputMode="decimal" placeholder="38" />
                </label>
                <label>
                  <span>Площадь до</span>
                  <input {...form.register("areaMax")} inputMode="decimal" placeholder="70" />
                </label>
                <label>
                  <span>Районы</span>
                  <select {...form.register("districts")}>
                    <option value="">Выберите район</option>
                    <option value="Центр">Центр</option>
                    <option value="ФМР">ФМР</option>
                    <option value="ЮМР">ЮМР</option>
                    <option value="Панорама">Панорама</option>
                    <option value="Черемушки">Черемушки</option>
                  </select>
                </label>
                <label>
                  <span>Срок сдачи до</span>
                  <select {...form.register("completionYearMax")}>
                    <option value="">Не важно</option>
                    <option value="2026">2026</option>
                    <option value="2027">2027</option>
                    <option value="2028">2028</option>
                  </select>
                </label>
                <label>
                  <span>Отделка</span>
                  <select {...form.register("finishing")}>
                    <option value="">Не важно</option>
                    <option value="без отделки">Без отделки</option>
                    <option value="предчистовая">Предчистовая</option>
                    <option value="чистовая">Чистовая</option>
                  </select>
                </label>
                <label>
                  <span>Этаж не ниже</span>
                  <select {...form.register("floorMin")}>
                    <option value="">Не важно</option>
                    <option value="1">1</option>
                    <option value="2">2</option>
                    <option value="3">3</option>
                    <option value="5">5</option>
                  </select>
                </label>
                <label>
                  <span>Этаж не выше</span>
                  <select {...form.register("floorMax")}>
                    <option value="">Не важно</option>
                    <option value="5">5</option>
                    <option value="9">9</option>
                    <option value="16">16</option>
                    <option value="25">25</option>
                  </select>
                </label>
              </>
            ) : (
              <>
                <label>
                  <span>Площадь дома от</span>
                  <input {...form.register("houseAreaMin")} inputMode="decimal" placeholder="100" />
                </label>
                <label>
                  <span>Площадь дома до</span>
                  <input {...form.register("houseAreaMax")} inputMode="decimal" placeholder="160" />
                </label>
                <label>
                  <span>Площадь участка от</span>
                  <input {...form.register("landAreaMin")} inputMode="decimal" placeholder="5" />
                </label>
                <label>
                  <span>Площадь участка до</span>
                  <input {...form.register("landAreaMax")} inputMode="decimal" placeholder="8" />
                </label>
                <label className="span-2">
                  <span>Локация / район / поселок</span>
                  <select {...form.register("settlementNames")}>
                    <option value="">Выберите локацию</option>
                    <option value="Немецкая деревня">Немецкая деревня</option>
                    <option value="Яблоновский">Яблоновский</option>
                    <option value="Энем">Энем</option>
                    <option value="Северный">Северный</option>
                  </select>
                </label>
                <label>
                  <span>Количество этажей от</span>
                  <input {...form.register("floorsCountMin")} inputMode="numeric" placeholder="1" />
                </label>
                <label>
                  <span>Количество этажей до</span>
                  <input {...form.register("floorsCountMax")} inputMode="numeric" placeholder="2" />
                </label>
                <label>
                  <span>Спален от</span>
                  <input {...form.register("bedroomsMin")} inputMode="numeric" placeholder="3" />
                </label>
                <label>
                  <span>Материал дома</span>
                  <select {...form.register("houseMaterial")}>
                    <option value="">Не важно</option>
                    <option value="кирпич">Кирпич</option>
                    <option value="монолит">Монолит</option>
                    <option value="газоблок">Газоблок</option>
                    <option value="дерево">Дерево</option>
                  </select>
                </label>
                <div className="checkbox-grid span-2">
                  {communicationOptions.map((item) => (
                    <label className="checkbox" key={item}>
                      <input type="checkbox" value={item} {...form.register("communications")} />
                      <span>{item}</span>
                    </label>
                  ))}
                </div>
              </>
            )}
          </div>
        </section>

        <section className="panel form-section">
          <div className="form-section__header">
            <h2>Комментарий</h2>
            <span>Важные пожелания клиента</span>
          </div>
          <label>
            <span>Комментарий</span>
            <textarea
              {...form.register("comment")}
              placeholder={isHouse ? "Нужен готовый дом с участком от 5 соток и нормальным подъездом." : "Нужна квартира для семьи рядом со школой и без первого этажа."}
            />
          </label>
        </section>

        {createClient.error ? <div className="form-error">{createClient.error.message}</div> : null}

        <div className="form-actions">
          <Link className="button" to="/clients">Отмена</Link>
          <button className="button button--primary" disabled={submitDisabled} type="submit">
            {createClient.isPending ? <Loader2 className="spin" size={18} /> : <Check size={18} />}
            Создать и найти объекты
          </button>
        </div>
      </form>
    </div>
  );
}
