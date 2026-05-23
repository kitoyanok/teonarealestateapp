// Этот компонент показывает пустое состояние.
// Проще говоря: он нужен, когда в разделе пока нет клиентов, объектов или результатов поиска.

import type { ReactNode } from "react";

type Props = {
  title: string;
  text: string;
  action?: ReactNode;
};

export function EmptyState({ title, text, action }: Props) {
  return (
    <div className="empty-state">
      <div className="empty-state__mark" />
      <h3>{title}</h3>
      <p>{text}</p>
      {action}
    </div>
  );
}
