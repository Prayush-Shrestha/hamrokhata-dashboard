import { formatStatus, getStatusClass } from "../utils/dashboardHelpers";

export default function TaskRow({ task }) {
  const statusClass = getStatusClass(task.status);
  const priorityClass = String(task.priority || "medium").toLowerCase();

  return (
    <div className="task-row">
      <div className="task-info">
        <span className={`task-dot ${statusClass}`} />
        <div>
          <strong>{task.title || "Untitled task"}</strong>
          <small>{task.assignee_name || "Unassigned"}</small>
        </div>
      </div>
      <span className={`priority ${priorityClass}`}>{formatStatus(task.priority)}</span>
      <span className={`task-status ${statusClass}`}>{formatStatus(task.status)}</span>
      <span className="task-date">{task.due_date || "No due date"}</span>
    </div>
  );
}
