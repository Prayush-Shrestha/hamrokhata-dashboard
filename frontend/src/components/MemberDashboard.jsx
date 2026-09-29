import { formatStatus, getInitials } from "../utils/dashboardHelpers";

function PanelHeader({ title, subtitle, right }) {
  return (
    <div className="panel-header">
      <div>
        <h2>{title}</h2>
        {subtitle && <p>{subtitle}</p>}
      </div>
      {right && <span>{right}</span>}
    </div>
  );
}

export default function MemberDashboard({ employees, tasks }) {
  return (
    <section className="dashboard-panel member-panel">
      <PanelHeader
        title="Workspace member dashboard"
        subtitle="One simple view of each member's tasks and completion time"
        right={`${employees.length} members`}
      />
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>MEMBER</th><th>TASKS</th><th>AVERAGE</th><th>TOTAL TIME</th>
              <th>LATEST ASSIGNED TASK</th><th>WORK STARTED</th><th>TRACKED TIME</th>
            </tr>
          </thead>
          <tbody>
            {employees.length === 0 ? (
              <tr><td colSpan="7" className="empty">No members found.</td></tr>
            ) : (
              employees.map((employee, i) => {
                const memberTasks = [];
                for (const t of tasks) {
                  if (t.assignee_name === employee.name) memberTasks.push(t);
                }
                const latestTask = memberTasks[0];

                return (
                  <tr key={`${employee.name}-${i}`}>
                    <td>
                      <div className="member">
                        <div className={`member-avatar ${i % 2 === 0 ? "purple" : "green"}`}>{getInitials(employee.name)}</div>
                        <div>
                          <strong>{employee.name}</strong>
                          <small>{i === 0 ? "Owner" : "Member"}</small>
                        </div>
                      </div>
                    </td>
                    <td>
                      <b>{employee.assigned || 0}</b> <span>assigned</span>
                      <small>{employee.remaining || 0} active · {employee.completed || 0} done</small>
                    </td>
                    <td>—</td>
                    <td>0m</td>
                    <td>
                      <strong>{latestTask?.title || "Nothing assigned"}</strong>
                      <small>{latestTask ? formatStatus(latestTask.status) : ""}</small>
                    </td>
                    <td>{latestTask ? "Not started" : "—"}</td>
                    <td>
                      <span className="assigned">Assigned</span>
                      <small>Not tracked</small>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
