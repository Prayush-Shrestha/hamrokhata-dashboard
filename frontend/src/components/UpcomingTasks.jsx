import TaskRow from "./TaskRow";

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

export default function UpcomingTasks({ tasks }) {
  return (
    <section className="dashboard-panel">
      <PanelHeader title="Upcoming tasks" subtitle="Tasks currently in the workspace" right={`${tasks.length} tasks`} />
      <div className="task-list">
        {tasks.length === 0 ? (
          <div className="empty">No tasks found.</div>
        ) : (
          tasks.slice(0, 7).map((task) => <TaskRow key={task.id} task={task} />)
        )}
      </div>
    </section>
  );
}
