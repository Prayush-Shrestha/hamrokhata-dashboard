export default function ChartCard({ title, subtitle, chart, alt }) {
  return (
    <section className="dashboard-panel chart-card">
      <div className="chart-card-head">
        <h2>{title}</h2>
        {subtitle && <p>{subtitle}</p>}
      </div>

      {chart ? (
        <img src={chart} alt={alt || title} className="backend-chart" />
      ) : (
        <div className="chart-card-empty">No chart available</div>
      )}
    </section>
  );
}
