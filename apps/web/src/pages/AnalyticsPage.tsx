import { BarChart3 } from "lucide-react";

export function AnalyticsPage() {
  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Аналитика</h1>
          <p>Сводка по клиентам, подборкам и активности.</p>
        </div>
      </header>

      <section className="panel analytics-placeholder">
        <div className="analytics-icon"><BarChart3 size={34} /></div>
        <h2>Раздел в подготовке</h2>
        <p>Здесь появятся активность по клиентам, популярные районы, конверсия подборок и динамика найденных объектов.</p>
      </section>
    </div>
  );
}
