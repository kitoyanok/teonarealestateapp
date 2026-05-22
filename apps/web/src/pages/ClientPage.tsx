import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Copy, ExternalLink, Loader2, Phone, RefreshCw, Send, Trash2, X } from "lucide-react";
import { useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import type { Client, FoundProperty, Property, ShortlistItem } from "../entities/types";
import { api } from "../shared/api";
import {
  formatCompactMoney,
  formatMoney,
  hasRealPropertyImage,
  profileSummary,
  propertyDescription,
  propertyDistrictLabel,
  propertyMeta,
  propertySourceLabel,
  propertyTitle
} from "../shared/format";
import { EmptyState } from "../widgets/EmptyState";
import { StatusBadge } from "../widgets/StatusBadge";

function PropertyMedia({ property }: { property: Property }) {
  const image = hasRealPropertyImage(property) ? property.images?.[0] : undefined;
  if (image) {
    return <img src={image} alt={propertyTitle(property)} loading="lazy" />;
  }
  return (
    <div className="property-image-empty property-image-empty--detailed">
      <strong>Фото не найдено</strong>
      <span>Откройте источник, чтобы посмотреть изображения на сайте застройщика.</span>
    </div>
  );
}

function PropertyCard({
  item,
  inShortlist,
  onOpen,
  onAdd
}: {
  item: FoundProperty;
  inShortlist: boolean;
  onOpen: (property: Property) => void;
  onAdd: (propertyId: string) => void;
}) {
  const property = item.property;
  const filledSegments = Math.max(1, Math.min(5, Math.ceil((item.matchScore ?? 0) / 20)));
  return (
    <article className="property-card">
      <div className="property-card__body">
        <h3>{propertyTitle(property)}</h3>
        <p className="property-card__source">{propertySourceLabel(property)}</p>
        <strong className="price">{formatMoney(property.price)}</strong>
        <div className="property-card__meta">
          <span>{propertyMeta(property) || "Параметры уточняются"}</span>
        </div>
        <p className="property-card__description">{propertyDescription(property)}</p>
        <div className="match-row">
          <span>Совпадение: {item.matchScore ?? 0}%</span>
          <div>
            {Array.from({ length: 5 }, (_, index) => (
              <i key={index} className={index < filledSegments ? "is-filled" : undefined} />
            ))}
          </div>
        </div>
        <div className="card-actions">
          <button className="button button--row button--light" type="button" onClick={() => onOpen(property)}>Подробнее</button>
          <button
            className={`button button--row property-card__cta ${inShortlist ? "button--success" : "button--primary"}`}
            type="button"
            onClick={() => !inShortlist && onAdd(property.id)}
          >
            {inShortlist ? "В подборке" : "В подборку"}
          </button>
        </div>
      </div>
    </article>
  );
}

function PropertyDrawer({
  property,
  inShortlist,
  match,
  onClose,
  onAdd,
  onRemove
}: {
  property: Property;
  inShortlist: boolean;
  match?: FoundProperty;
  onClose: () => void;
  onAdd: () => void;
  onRemove: () => void;
}) {
  const safeRooms = property.rooms !== null && property.rooms !== undefined && property.rooms >= 0 && property.rooms <= 8
    ? property.rooms
    : null;
  const district = propertyDistrictLabel(property);
  return (
    <div className="drawer-backdrop" onClick={onClose}>
      <aside className="property-drawer" onClick={(event) => event.stopPropagation()}>
        <div className="drawer-header">
          <div>
            <h2>{propertyTitle(property)}</h2>
          <p>{propertyMeta(property) || propertySourceLabel(property)}</p>
        </div>
          <button className="icon-button" type="button" onClick={onClose} aria-label="Закрыть">
            <X size={18} />
          </button>
        </div>

        <div className="drawer-media">
          <PropertyMedia property={property} />
        </div>

        <div className="drawer-price">
          <strong>{formatMoney(property.price)}</strong>
          {property.pricePerMeter ? <span>{formatMoney(property.pricePerMeter)}/м²</span> : null}
        </div>

        <div className="details-grid">
          {(property.propertyType === "house"
            ? [
                ["Дом", property.houseArea ? `${property.houseArea} м²` : null],
                ["Участок", property.landArea ? `${property.landArea} сот.` : null],
                ["Район", district],
                ["Этажей", property.houseFloors],
                ["Спален", property.bedrooms],
                ["Материал", property.houseMaterial],
                ["Коммуникации", property.communications?.join(", ")]
              ]
            : [
                ["Площадь", property.area ? `${property.area} м²` : null],
                ["Комнат", safeRooms === 0 ? "Студия" : safeRooms],
                ["Район", district],
                ["Этаж", property.floor && property.floorsTotal ? `${property.floor}/${property.floorsTotal}` : null],
                ["Срок сдачи", property.completionYear],
                ["Отделка", property.finishing],
                ["Источник", property.sourceName]
              ]).map(([label, value]) => value ? (
            <div key={String(label)}>
              <span>{label}</span>
              <strong>{value}</strong>
            </div>
          ) : null)}
        </div>

        {(match?.matchReasons?.length || match?.mismatchReasons?.length) ? (
          <section className="drawer-section">
            <h3>Подходит по параметрам</h3>
            <div className="reason-list">
              {(match?.matchReasons ?? []).map((reason) => <span className="reason reason--ok" key={reason}>{reason}</span>)}
              {(match?.mismatchReasons ?? []).map((reason) => <span className="reason reason--warn" key={reason}>{reason}</span>)}
            </div>
          </section>
        ) : null}

        <section className="drawer-section">
          <h3>Описание</h3>
          <p>{propertyDescription(property)}</p>
        </section>

        <div className="drawer-actions">
          {inShortlist ? (
            <button className="button button--danger" type="button" onClick={onRemove}>Убрать из подборки</button>
          ) : (
            <button className="button button--primary" type="button" onClick={onAdd}>Добавить в подборку</button>
          )}
          <a className="button button--light" href={property.sourceUrl} target="_blank" rel="noreferrer">
            <ExternalLink size={16} />
            Открыть источник
          </a>
        </div>
      </aside>
    </div>
  );
}

function ShareModal({
  client,
  text,
  onClose,
  onCopied
}: {
  client: Client;
  text: string;
  onClose: () => void;
  onCopied: () => void;
}) {
  const phone = client.phone || client.sendContact || "";

  const copyText = async () => {
    await navigator.clipboard.writeText(text);
    onCopied();
  };

  const copyPhone = async () => {
    if (!phone) return;
    await navigator.clipboard.writeText(phone);
  };

  return (
    <div className="modal-backdrop">
      <section className="share-modal">
        <div className="drawer-header">
          <div>
            <h2>Отправка подборки</h2>
            <p>{client.name}{phone ? ` · ${phone}` : ""}</p>
          </div>
          <div className="modal-actions modal-actions--inline">
            <button className="icon-button" type="button" onClick={copyText} aria-label="Скопировать текст">
              <Copy size={18} />
            </button>
            <button className="icon-button" type="button" onClick={onClose} aria-label="Закрыть">
              <X size={18} />
            </button>
          </div>
        </div>

        <div className="share-toolbar">
          <button className="button button--light" type="button" onClick={copyPhone}>
            <Phone size={16} />
            Скопировать телефон
          </button>
          <button className="button button--primary" type="button" onClick={copyText}>
            <Copy size={16} />
            Скопировать текст
          </button>
        </div>

        <textarea className="message-preview" readOnly value={text} />
      </section>
    </div>
  );
}

export function ClientPage() {
  const { id } = useParams();
  const queryClient = useQueryClient();
  const [selectedProperty, setSelectedProperty] = useState<Property | null>(null);
  const [shareText, setShareText] = useState("");

  const clientQuery = useQuery({
    queryKey: ["client", id],
    queryFn: () => api.get<Client>(`/api/clients/${id}`),
    enabled: Boolean(id)
  });

  const invalidate = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ["client", id] }),
      queryClient.invalidateQueries({ queryKey: ["clients"] }),
      queryClient.invalidateQueries({ queryKey: ["dashboard"] })
    ]);
  };

  const addToShortlist = useMutation({
    mutationFn: (propertyId: string) => api.post(`/api/clients/${id}/shortlist/${propertyId}`),
    onSuccess: invalidate
  });
  const removeFromShortlist = useMutation({
    mutationFn: (propertyId: string) => api.delete(`/api/clients/${id}/shortlist/${propertyId}`),
    onSuccess: invalidate
  });
  const refreshSearch = useMutation({
    mutationFn: () => api.post(`/api/clients/${id}/search`),
    onSuccess: invalidate
  });
  const share = useMutation({
    mutationFn: () => api.post<{ messageText: string }>(`/api/clients/${id}/share-message`),
    onSuccess: (payload) => setShareText(payload.messageText)
  });
  const markSent = useMutation({
    mutationFn: () => api.post(`/api/clients/${id}/mark-sent`),
    onSuccess: invalidate
  });

  const client = clientQuery.data;
  const shortlistIds = useMemo(() => new Set((client?.shortlistItems ?? []).map((item: ShortlistItem) => item.propertyId)), [client?.shortlistItems]);
  const selectedMatch = client?.foundProperties?.find((item) => item.propertyId === selectedProperty?.id);

  if (clientQuery.isLoading) {
    return <div className="page"><div className="boot-screen">Загружаем карточку клиента...</div></div>;
  }

  if (!client) {
    return (
      <div className="page">
        <EmptyState title="Клиент не найден" text="Проверьте ссылку или вернитесь к списку клиентов." action={<Link className="button" to="/clients">К клиентам</Link>} />
      </div>
    );
  }

  const found = client.foundProperties ?? [];
  const shortlist = client.shortlistItems ?? [];

  return (
    <div className="page client-page">
      <header className="page-header page-header--compact">
        <div>
          <Link className="back-link" to="/clients"><ArrowLeft size={16} /> Клиенты</Link>
          <h1>{client.name}</h1>
          <p>{profileSummary(client)}</p>
        </div>
        <div className="header-actions">
          <button className="button button--light" disabled={refreshSearch.isPending} type="button" onClick={() => refreshSearch.mutate()}>
            {refreshSearch.isPending ? <Loader2 className="spin" size={16} /> : <RefreshCw size={16} />}
            Обновить поиск
          </button>
        </div>
      </header>

      <section className="dashboard-grid dashboard-grid--client">
        <article className="panel panel--wide panel--client-meta">
          <div className="client-card__title">
            <h2>Параметры клиента</h2>
            <StatusBadge status={client.status} />
          </div>
          <div className="client-info-grid">
            <span>Телефон <strong>{client.phone || "Не указан"}</strong></span>
            <span>Тип <strong>{client.propertyType === "house" ? "Дом" : "Квартира"}</strong></span>
            <span>Бюджет <strong>{formatMoney(client.searchProfile?.budgetMin)} — {formatMoney(client.searchProfile?.budgetMax)}</strong></span>
            {client.propertyType === "apartment" ? (
              <>
                <span>Комнаты <strong>{client.searchProfile?.roomsMin ?? "Студия"}-{client.searchProfile?.roomsMax ?? "4+"}</strong></span>
                <span>Площадь <strong>от {client.searchProfile?.areaMin ?? "не указано"} м²</strong></span>
                <span>Локация <strong>{client.searchProfile?.districts?.join(", ") || "Любая"}</strong></span>
              </>
            ) : (
              <>
                <span>Дом <strong>от {client.searchProfile?.houseAreaMin ?? "не указано"} м²</strong></span>
                <span>Участок <strong>от {client.searchProfile?.landAreaMin ?? "не указано"} сот.</strong></span>
                <span>Локация <strong>{client.searchProfile?.settlementNames?.join(", ") || client.searchProfile?.districts?.join(", ") || "Любая"}</strong></span>
              </>
            )}
          </div>
          <div className="client-summary-tiles">
            <div className="client-summary-card client-summary-card--metric">
              <span>В подборке</span>
              <strong>{shortlist.length} объекта</strong>
            </div>
            <div className="client-summary-card client-summary-card--metric">
              <span>Найдено</span>
              <strong>{found.length} объекта</strong>
            </div>
          </div>
          {client.comment ? <p className="client-comment">{client.comment}</p> : null}
        </article>

        <aside className="panel panel--shortlist" id="share-shortlist">
          <div className="panel__header">
            <div>
              <h2>Подборка</h2>
              <p>{shortlist.length} объекта</p>
            </div>
            <button className="button button--light button--small" disabled={!shortlist.length} type="button" onClick={() => share.mutate()}>
              <Send size={14} />
              Отправить
            </button>
          </div>
          <div className="shortlist-list">
            {shortlist.length ? shortlist.map((item) => (
              <div className="shortlist-item" key={item.id}>
                <div>
                  <strong>{propertyTitle(item.property)}</strong>
                  <span>{formatCompactMoney(item.property.price)} · {propertyMeta(item.property)}</span>
                </div>
                <div className="shortlist-item__actions">
                  <button className="button button--row button--light" type="button" onClick={() => setSelectedProperty(item.property)}>
                    Открыть
                  </button>
                  <button className="icon-button" type="button" onClick={() => removeFromShortlist.mutate(item.propertyId)} aria-label="Удалить">
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            )) : (
              <div className="empty-inline compact">
                <h3>Подборка пока пустая</h3>
                <p>Откройте найденные объекты и добавьте подходящие варианты.</p>
              </div>
            )}
          </div>
          <div className="client-summary-card">
            <div><span>Телефон</span><strong>{client.phone || "Не указан"}</strong></div>
            <div><span>Статус</span><StatusBadge status={client.status} /></div>
          </div>
        </aside>
      </section>

      <section className="panel found-properties-section">
        <div className="panel__header">
          <div>
            <h2>Найденные объекты</h2>
            <p>{found.length} вариантов по параметрам клиента</p>
          </div>
        </div>

        {client.status === "searching" ? (
          <section className="search-state">
            <Loader2 className="spin" size={24} />
            <h2>Ищем объекты под запрос клиента...</h2>
            <p>{profileSummary(client)}</p>
          </section>
        ) : client.status === "no_results" ? (
          <EmptyState
            title="Объекты не найдены"
            text="Попробуйте изменить параметры клиента или обновить поиск позже."
            action={<button className="button button--primary" type="button" onClick={() => refreshSearch.mutate()}>Повторить поиск</button>}
          />
        ) : client.status === "error" ? (
          <EmptyState
            title="Не удалось выполнить поиск"
            text={client.searchRuns?.[0]?.errorMessage || "Проверьте подключение или попробуйте позже."}
            action={<button className="button button--primary" type="button" onClick={() => refreshSearch.mutate()}>Повторить</button>}
          />
        ) : found.length ? (
          <div className="properties-grid-scroll">
          <div className="property-grid">
            {found.map((item) => (
              <PropertyCard
                item={item}
                inShortlist={shortlistIds.has(item.propertyId)}
                key={item.id}
                onOpen={setSelectedProperty}
                onAdd={(propertyId) => addToShortlist.mutate(propertyId)}
              />
            ))}
          </div>
          </div>
        ) : (
          <EmptyState
            title="Объекты не найдены"
            text="Попробуйте изменить параметры клиента или повторить поиск позже."
            action={<button className="button button--primary" type="button" onClick={() => refreshSearch.mutate()}>Повторить поиск</button>}
          />
        )}
      </section>

      {selectedProperty ? (
        <PropertyDrawer
          property={selectedProperty}
          match={selectedMatch}
          inShortlist={shortlistIds.has(selectedProperty.id)}
          onClose={() => setSelectedProperty(null)}
          onAdd={() => addToShortlist.mutate(selectedProperty.id)}
          onRemove={() => removeFromShortlist.mutate(selectedProperty.id)}
        />
      ) : null}

      {shareText ? (
        <ShareModal
          client={client}
          text={shareText}
          onClose={() => setShareText("")}
          onCopied={() => markSent.mutate()}
        />
      ) : null}
    </div>
  );
}
