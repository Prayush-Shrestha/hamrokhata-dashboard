function StatisticCard({ title, value, subtitle }) {
  return (
    <div className="stat-card">
      <span className="stat-title">{title}</span>
      <strong>{value}</strong>
      <small>{subtitle}</small>
    </div>
  );
}

export default function Statistics({
  memberCount,
  dueSoon,
  totalTasks,
  completionPercentage,
  activeAssignments,
}) {
  return (
    <section className="statistics-grid">
      <StatisticCard title="Members" value={memberCount} subtitle="Active workspace members" />
      <StatisticCard title="Due soon" value={dueSoon} subtitle="Next 7 days" />
      <StatisticCard title="Total tasks" value={totalTasks} subtitle="Including completed tasks" />
      <StatisticCard title="Average completion" value={`${completionPercentage}%`} subtitle="Overall completion" />
      <StatisticCard title="Active assignments" value={activeAssignments} subtitle="Assigned, running or paused" />
    </section>
  );
}
