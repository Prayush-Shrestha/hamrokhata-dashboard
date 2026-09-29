import StatusChart from "./StatusChart";
import PriorityChart from "./PriorityChart";
import WorkloadChart from "./WorkloadChart";
import TimelineChart from "./TimelineChart";

export default function Charts({ charts }) {
  const data = charts || {};

  return (
    <section className="charts-grid">
      <StatusChart chart={data.status} />
      <PriorityChart chart={data.priority} />
      <WorkloadChart chart={data.workload} />
      <TimelineChart chart={data.timeline} />
    </section>
  );
}
