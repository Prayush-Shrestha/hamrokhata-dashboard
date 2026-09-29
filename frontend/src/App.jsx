import { useEffect, useState } from "react";
import "./App.css";

import Header from "./components/Header";
import MetricCard from "./components/MetricCard";
import Charts from "./components/Charts";
import Statistics from "./components/Statistics";
import MemberDashboard from "./components/MemberDashboard";
import UpcomingTasks from "./components/UpcomingTasks";
import RecentActivity from "./components/RecentActivity";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export default function App() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadDashboard() {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_URL}/api/dashboard`, { cache: "no-store" });
      if (!res.ok) {
        throw new Error("Dashboard request failed: " + res.status);
      }
      const json = await res.json();
      setDashboard(json);
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  if (loading) {
    return (
      <div className="loading">
        <div className="loading-box"><strong>Loading dashboard...</strong></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-screen">
        <div className="error-box">
          <div className="error-icon">!</div>
          <h2>Unable to load dashboard</h2>
          <p>{error}</p>
          <button className="retry-button" onClick={loadDashboard}>Try Again</button>
        </div>
      </div>
    );
  }

  const summary = dashboard?.summary || {};
  const tasks = dashboard?.tasks || [];
  const employees = dashboard?.employees || [];
  const charts = dashboard?.charts || {};

  const totalTasks = Number(summary.total_tasks || 0);
  const completed = Number(summary.completed || 0);
  const openTasks = Math.max(totalTasks - completed, 0);
  const completionPercentage = Number(summary.completion_percentage || 0);

  // count tasks due in the next 7 days
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const nextSevenDays = new Date(today);
  nextSevenDays.setDate(nextSevenDays.getDate() + 7);

  let dueSoon = 0;
  for (const t of tasks) {
    if (!t.due_date || t.status === "completed" || t.status === "done") continue;
    const due = new Date(t.due_date + "T00:00:00");
    if (due >= today && due <= nextSevenDays) dueSoon++;
  }

  let activeAssignments = 0;
  for (const e of employees) {
    activeAssignments += Number(e.remaining || 0);
  }

  return (
    <main className="dashboard-page">
      <div className="dashboard-container">
        <Header onRefresh={loadDashboard} />

        <section className="top-cards">
          <MetricCard title="Completion rate" value={`${completionPercentage}%`} subtitle={`${completed} of ${totalTasks} tasks completed`} type="completion" progress={completionPercentage} />
          <MetricCard title="Open tasks" value={openTasks} subtitle="Across this workspace" />
          <MetricCard title="Completed" value={completed} subtitle="Database total" type="success" />
          <MetricCard title="Overdue" value={summary.overdue || 0} subtitle="Needs attention" type="danger" />
        </section>

        <Charts charts={charts} />

        <Statistics
          memberCount={employees.length}
          dueSoon={dueSoon}
          totalTasks={totalTasks}
          completionPercentage={completionPercentage}
          activeAssignments={activeAssignments}
        />

        <MemberDashboard employees={employees} tasks={tasks} />

        <section className="bottom-grid">
          <UpcomingTasks tasks={tasks} />
          <RecentActivity activities={dashboard?.recent_activity || []} />
        </section>
      </div>
    </main>
  );
}
