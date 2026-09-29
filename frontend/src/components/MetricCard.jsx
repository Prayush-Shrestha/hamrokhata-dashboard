export default function MetricCard({ title, value, subtitle, type = "", progress }) {
  let barWidth = progress || 0;
  if (barWidth < 0) barWidth = 0;
  if (barWidth > 100) barWidth = 100;

  return (
    <div className="metric-card">
      <div className="card-title-row">
        <span className="card-title">{title}</span>
        <span className="dots">•••</span>
      </div>
      <div className={`metric-value ${type}`}>{value}</div>
      <div className={`metric-subtitle ${type}`}>{subtitle}</div>
      {type === "completion" && (
        <div className="completion-bar">
          <div className="completion-fill" style={{ width: barWidth + "%" }} />
        </div>
      )}
    </div>
  );
}
