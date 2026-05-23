// Этот маленький компонент показывает статус в аккуратной плашке.
// Проще говоря: он переводит внутренний код статуса в понятный текст и цвет.

import { statusLabel } from "../shared/format";

type Props = {
  status: string;
};

export function StatusBadge({ status }: Props) {
  return <span className={`status status-${status}`}>{statusLabel[status] ?? status}</span>;
}
