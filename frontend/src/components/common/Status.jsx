import {STATUS_LABELS} from '../../utils/format.js';

export default function StatusBadge({status}) {
  return <span className={`pay-badge pay-badge-${status}`}>{STATUS_LABELS[status] || status}</span>;
}
