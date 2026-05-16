import { useQuery } from "@tanstack/react-query";
import { ArrowUpRight, BriefcaseBusiness, ChartColumnBig, ClipboardList, House, TrendingDown, TrendingUp } from "lucide-react";
import { Link } from "react-router-dom";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { ActivityPoint, Client, DashboardSummary } from "../entities/types";
import { api } from "../shared/api";
import { profileSummary } from "../shared/format";
import { StatusBadge } from "../widgets/StatusBadge";

const kpiConfig = [
  { key: "clientsInWork", title: "Клиенты в работе", icon: BriefcaseBusiness, trend: "+8.4%", positive: true },
  { key: "foundObjects", title: "Найдено объектов", icon: House, trend: "-3.7%", positive: false },
  { key: "shortlistItems", title: "В подборках", icon: ClipboardList, trend: "+8.4%", positive: true },
  { key: "readyToSend", title: "Готово к отправке", icon: ChartColumnBig, trend: "+8.4%", positive: true }
] as const;

const demoBars = [
  [8, 8, 8, 8, 8, 8, 8, 8, 8, 4, 4, 4],
  [2, 3, 2, 5, 4, 3, 4, 7, 6, 6, 3, 4],
  [4, 3, 6, 5, 4, 7, 6, 8, 5, 4, 8, 7],
  [7, 7, 7, 7, 7, 7, 7, 7, 7, 4, 4, 4]
];

function MiniBars({ values, accentIndex }: { values: number[]; accentIndex?: number }) {
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
          const TrendIcon = item.positive ? TrendingUp : TrendingDown;
          return (
            <article className="kpi-card" key={item.key}>
              <div className="kpi-card__head">
                <strong>{summary.data?.[item.key] ?? 0}</strong>
                <span className={`trend ${item.positive ? "is-up" : "is-down"}`}>
                  <TrendIcon size={12} />
                  {item.trend}
                </span>
              </div>
              <MiniBars values={demoBars[index]} accentIndex={index === 2 ? 11 : undefined} />
              <div className="kpi-card__label">
                <Icon size={15} />
                <span>{item.title}</span>
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
              <p>С кем продолжить работу</p>
            </div>
          </div>
          {activity.data?.some((point) => point.found > 0) ? (
            <div className="chart-frame chart-frame--soft">
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={activity.data}>
                  <CartesianGrid stroke="#F0F0F0" vertical={false} />
                  <XAxis dataKey="label" stroke="#B2B2B2" tickLine={false} axisLine={false} />
                  <YAxis stroke="#B2B2B2" tickLine={false} axisLine={false} width={28} />
                  <Tooltip
                    contentStyle={{
                      background: "#FFFFFF",
                      border: "1px solid #E7E7E7",
                      borderRadius: 12,
                      boxShadow: "0 12px 40px rgba(0, 0, 0, 0.08)"
                    }}
                  />
                  <Line type="monotone" dataKey="found" stroke="#FD6000" strokeWidth={3} dot={false} />
                  <Line type="monotone" dataKey="shortlisted" stroke="#FFC49F" strokeWidth={2} dot={false} />
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
