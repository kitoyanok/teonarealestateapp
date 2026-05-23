// Эта страница показывает всех клиентов риелтора.
// Проще говоря: здесь можно найти нужную карточку, отфильтровать список и перейти в детали клиента.

import { useQuery } from "@tanstack/react-query";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useMemo } from "react";
import type { Client } from "../entities/types";
import { api } from "../shared/api";
import { profileSummary } from "../shared/format";
import { EmptyState } from "../widgets/EmptyState";
import { StatusBadge } from "../widgets/StatusBadge";

export function ClientsPage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const search = searchParams.get("search") ?? "";
  const status = searchParams.get("status") ?? "";
  const query = useMemo(() => new URLSearchParams({ ...(search ? { search } : {}), ...(status ? { status } : {}) }).toString(), [search, status]);
  const clients = useQuery({
    queryKey: ["clients", query],
    queryFn: () => api.get<Client[]>(`/api/clients${query ? `?${query}` : ""}`)
  });

  return (
    <div className="page">
      <section className="panel panel--page-title">
        <div className="panel__header">
          <div>
            <h2>Все клиенты</h2>
            <p>Все заявки и параметры поиска в одном списке</p>
          </div>
          <select
            className="compact-select"
            value={status}
            onChange={(event) => setSearchParams({ ...(search ? { search } : {}), ...(event.target.value ? { status: event.target.value } : {}) })}
          >
            <option value="">Все статусы</option>
          <option value="found">Найдены объекты</option>
          <option value="shortlist_ready">Подборка готова</option>
          <option value="no_results">Нет объектов</option>
          <option value="error">Ошибка поиска</option>
          </select>
        </div>
      </section>

      <section className="panel">
        {clients.data?.length ? (
          <div className="clients-table-card">
            <div className="table-wrap clients-table-scroll clients-table">
            <table className="table-sticky">
              <thead>
                <tr>
                  <th>Клиент</th>
                  <th>Тип</th>
                  <th>Телефон</th>
                  <th>Запрос</th>
                  <th>Найдено</th>
                  <th>В подборке</th>
                  <th>Статус</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {clients.data.map((client) => (
                  <tr key={client.id} onClick={() => navigate(`/clients/${client.id}`)} role="button" tabIndex={0}>
                    <td>{client.name}</td>
                    <td>{client.propertyType === "house" ? "Дом" : "Квартира"}</td>
                    <td>{client.phone || "Не указан"}</td>
                    <td>{profileSummary(client)}</td>
                    <td>{client._count?.foundProperties ?? 0}</td>
                    <td>{client._count?.shortlistItems ?? 0}</td>
                    <td><StatusBadge status={client.status} /></td>
                    <td>
                      <button className="button button--row" type="button" onClick={(event) => { event.stopPropagation(); navigate(`/clients/${client.id}`); }}>
                        Открыть
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            </div>
          </div>
        ) : (
          <EmptyState
            title="Клиентов пока нет"
            text="Добавьте первого клиента и запустите подбор недвижимости."
            action={<Link className="button button--primary" to="/clients/new">Добавить клиента</Link>}
          />
        )}
      </section>
    </div>
  );
}
