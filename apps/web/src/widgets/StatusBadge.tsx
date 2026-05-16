import { statusLabel } from "../shared/format";

type Props = {
  status: string;
};

export function StatusBadge({ status }: Props) {
  return <span className={`status status-${status}`}>{statusLabel[status] ?? status}</span>;
}
