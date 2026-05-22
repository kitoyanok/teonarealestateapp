import { useQuery } from "@tanstack/react-query";
import { ArrowUpRight, BriefcaseBusiness, ChartColumnBig, ClipboardList, House } from "lucide-react";
import { Link } from "react-router-dom";
import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { ActivityPoint, Client, DashboardSummary } from "../entities/types";
import { api } from "../shared/api";
import { profileSummary } from "../shared/format";
import { StatusBadge } from "../widgets/StatusBadge";

const kpiConfig = [
  { key: "clientsInWork", title: "Клиенты в работе", subtitle: "активные заявки", icon: BriefcaseBusiness, activityKey: "clients" },
  { key: "foundObjects", title: "Найдено объектов", subtitle: "по текущим клиентам", icon: House, activityKey: "found" },
  { key: "shortlistItems", title: "В подборках", subtitle: "отобрано вручную", icon: ClipboardList, activityKey: "shortlisted" },
  { key: "readyToSend", title: "Готово к отправке", subtitle: "можно отправить", icon: ChartColumnBig, activityKey: "ready" }
] as const;

function MiniLine({ values }: { values: number[] }) {
  const max = Math.max(...values, 0);
  if (max <= 0) {
    return null;
  }
  const min = Math.min(...values);
  const width = 260;
  const height = 78;
  const step = values.length > 1 ? width / (values.length - 1) : width;
  const points = values
    .map((value, index) => {
      const x = Math.round(index * step);
      const ratio = max === min ? 0.45 : (value - min) / (max - min);
      const y = Math.round(height - 12 - ratio * 52);
      return `${x},${y}`;
    })
    .join(" ");
  return (
    <div className="mini-line" aria-hidden="true">
      <svg viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none">
        <polyline points={points} />
      </svg>
    </div>
  );
}

function DashboardTooltip({ active, payload, label }: { active?: boolean; payload?: Array<{ value?: number }>; label?: string }) {
  if (!active || !payload?.length) {
    return null;
  }
  const foundValue = payload.find((item, index) => index === 0)?.value ?? 0;
  const shortlistValue = payload.find((item, index) => index === 1)?.value ?? 0;
  return (
    <div className="chart-tooltip">
      <strong>{label}</strong>
      <span>Найдено объектов: {foundValue}</span>
      <span>Добавлено в подборки: {shortlistValue}</span>
    </div>
  );
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
        {kpiConfig.map((item) => {
          const Icon = item.icon;
          const lineValues = activity.data?.length ? activity.data.map((point) => point[item.activityKey]) : [];
          return (
            <article className="kpi-card" key={item.key}>
              <div className="kpi-card__head">
                <strong>{summary.data?.[item.key] ?? 0}</strong>
              </div>
              {lineValues.some((value) => value > 0) ? <MiniLine values={lineValues} /> : null}
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
          {activity.data?.some((point) => point.found > 0 || point.shortlisted > 0 || point.sent > 0 || point.clients > 0) ? (
            <div className="chart-frame chart-frame--dashboard">
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={activity.data} margin={{ top: 8, right: 10, left: -8, bottom: 0 }}>
                  <CartesianGrid stroke="#F0F0F0" vertical={false} />
                  <XAxis dataKey="label" stroke="#8F8F8F" tickLine={false} axisLine={false} />
                  <YAxis stroke="#8F8F8F" tickLine={false} axisLine={false} allowDecimals={false} />
                  <Tooltip content={<DashboardTooltip />} cursor={{ fill: "rgba(253,96,0,0.06)" }} />
                  <Line dataKey="found" type="monotone" stroke="#FD6000" strokeWidth={4} dot={{ r: 4, fill: "#FD6000" }} activeDot={{ r: 6 }} />
                  <Bar dataKey="shortlisted" radius={[8, 8, 0, 0]} fill="#FFD6B8" barSize={20} />
                </LineChart>
              </ResponsiveContainer>
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
