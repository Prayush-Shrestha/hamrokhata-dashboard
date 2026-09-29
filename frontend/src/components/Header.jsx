export default function Header({ onRefresh }) {
  return (
    <section className="dashboard-header">
      <div>
        <div className="small-heading">HAMRO KHATA</div>
        <h1>Dashboard</h1>
        <p>One clear view of your team's work, progress and deadlines.</p>
      </div>
      <button className="refresh-button" onClick={onRefresh}>↻ Refresh</button>
    </section>
  );
}
