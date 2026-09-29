import { getInitials } from "../utils/dashboardHelpers";

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

export default function RecentActivity({ activities }) {
  return (
    <section className="dashboard-panel">
      <PanelHeader title="Recent activity" subtitle="Latest workspace updates" right="Latest updates" />
      <div className="activity-list">
        {activities.length === 0 ? (
          <div className="empty">No recent activity.</div>
        ) : (
          activities.slice(0, 7).map((activity, i) => (
            <div className="activity" key={`${activity.task_title}-${i}`}>
              <div className="activity-avatar">{getInitials(activity.user_name)}</div>
              <div>
                <p><strong>{activity.user_name}</strong> <span>created "{activity.task_title}"</span></p>
                <small>{activity.created_at}</small>
              </div>
            </div>
          ))
        )}
      </div>
    </section>
  );
}
