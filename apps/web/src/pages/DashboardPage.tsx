import { useQuery } from "@tanstack/react-query";
import { ArrowUpRight, BriefcaseBusiness, ChartColumnBig, ClipboardList, House } from "lucide-react";
import { Link } from "react-router-dom";
import type { ActivityPoint, Client, DashboardSummary } from "../entities/types";
import { api } from "../shared/api";
import { profileSummary } from "../shared/format";
import { StatusBadge } from "../widgets/StatusBadge";

const kpiConfig = [
  { key: "clientsInWork", title: "Клиенты в работе", subtitle: "активные заявки", icon: BriefcaseBusiness },
  { key: "foundObjects", title: "Найдено объектов", subtitle: "по текущим клиентам", icon: House },
  { key: "shortlistItems", title: "В подборках", subtitle: "отобрано вручную", icon: ClipboardList },
  { key: "readyToSend", title: "Готово к отправке", subtitle: "можно отправить", icon: ChartColumnBig }
] as const;

function MiniBars({ values, accentIndex }: { values: number[]; accentIndex: number }) {
  return (
    <div className="mini-bars" aria-hidden="true">
      {values.map((value, index) => (
        <span
          key={`${index}-${value}`}
          className={index === accentIndex ? "is-accent" : undefined}
          style={{ height: `${16 + value * 6}px` }}
        />
      ))}
    </div>
  );
}

function activityBars(points: ActivityPoint[]) {
  const values = points.map((point) => point.found);
  const max = Math.max(...values, 1);
  return values.map((value) => Math.max(2, Math.round((value / max) * 8)));
}

export function DashboardPage() {
  const summary = useQuery({
    queryKey: ["dashboard", "summary"],
    queryFn: () => api.get<DashboardSummary>("/api/dashboard/summary")
  });
  const activity = useQuery({
    queryKey: ["dashboard", "activity"],
    queryFn: () => api.get<ActivityPoint[]>("/api/dashboard/activity")
  });
  const attention = useQuery({
    queryKey: ["dashboard", "attention"],
    queryFn: () => api.get<Client[]>("/api/dashboard/attention-clients")
  });
  const clients = useQuery({
    queryKey: ["clients", "latest"],
    queryFn: () => api.get<Client[]>("/api/clients")
  });

  return (
    <div className="page dashboard-page">
      <section className="kpi-grid">
        {kpiConfig.map((item, index) => {
          const Icon = item.icon;
          const bars = activity.data?.length ? activityBars(activity.data) : Array.from({ length: 8 }, () => 4);
          return (
            <article className="kpi-card" key={item.key}>
              <div className="kpi-card__head">
                <strong>{summary.data?.[item.key] ?? 0}</strong>
              </div>
              <MiniBars values={bars} accentIndex={bars.length - 1} />
              <div className="kpi-card__label">
                <Icon size={15} />
                <div>
                  <span>{item.title}</span>
                  <small>{item.subtitle}</small>
                </div>
              </div>
            </article>
          );
        })}
      </section>

      <section className="dashboard-grid">
        <article className="panel panel--wide">
          <div className="panel__header">
            <div>
              <h2>Активность за 7 дней</h2>
              <p>Найденные объекты по дням</p>
            </div>
          </div>
          {activity.data?.some((point) => point.found > 0) ? (
            <div className="activity-bars-card">
              <div className="activity-bars">
                {activity.data.map((point, index) => {
                  const max = Math.max(...activity.data.map((item) => item.found), 1);
                  const height = 36 + Math.round((point.found / max) * 160);
                  return (
                    <div className="activity-bars__item" key={point.key}>
                      <span className={index === activity.data.length - 1 ? "is-accent" : undefined} style={{ height }} />
                      <small>{point.label}</small>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            <div className="empty-inline empty-inline--chart">
              <h3>Пока нет истории поиска</h3>
              <p>Когда вы добавите клиентов и запустите поиск, здесь появится активность за последние 7 дней.</p>
            </div>
          )}
        </article>

        <article className="panel">
          <div className="panel__header">
            <div>
              <h2>Клиенты требуют внимания</h2>
              <p>С кем продолжить работу</p>
            </div>
          </div>
          <div className="table-wrap table-wrap--compact">
            <table>
              <thead>
                <tr>
                  <th>Клиент</th>
                  <th>Найдено</th>
                  <th>В подборке</th>
                  <th>Статус</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {(attention.data ?? []).slice(0, 4).map((client) => (
                  <tr key={client.id}>
                    <td>{client.name}</td>
                    <td>{client._count?.foundProperties ?? 0}</td>
                    <td>{client._count?.shortlistItems ?? 0}</td>
                    <td><StatusBadge status={client.status} /></td>
                    <td>
                      <Link className="button button--row" to={`/clients/${client.id}`}>
                        Открыть
                      </Link>
                    </td>
                  </tr>
                ))}
                {!attention.isLoading && !attention.data?.length ? (
                  <tr>
                    <td colSpan={5}>
                      <div className="empty-inline compact">
                        <h3>Пусто</h3>
                        <p>Добавьте первого клиента, чтобы увидеть рабочую очередь.</p>
                      </div>
                    </td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </article>
      </section>

      <section className="panel">
        <div className="panel__header">
          <div>
            <h2>Последние клиенты</h2>
            <p>Быстрый переход в карточку клиента</p>
          </div>
        </div>
        <div className="table-wrap">
          <table>
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
              {(clients.data ?? []).slice(0, 6).map((client) => (
                <tr key={client.id}>
                  <td>{client.name}</td>
                  <td>{client.propertyType === "house" ? "Дом" : "Квартира"}</td>
                  <td>{client.phone || "Не указан"}</td>
                  <td>{profileSummary(client)}</td>
                  <td>{client._count?.foundProperties ?? 0}</td>
                  <td>{client._count?.shortlistItems ?? 0}</td>
                  <td><StatusBadge status={client.status} /></td>
                    <td>
                      <Link className="button button--row" to={`/clients/${client.id}`}>
                        Открыть
                        <ArrowUpRight size={14} />
                      </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
