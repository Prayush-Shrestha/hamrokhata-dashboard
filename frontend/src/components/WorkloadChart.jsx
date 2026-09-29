import ChartCard from "./ChartCard";

export default function WorkloadChart({ chart }) {
  return (
    <ChartCard
      title="Workload by member"
      subtitle="Compare assigned work so an admin can spot workload imbalance quickly."
      chart={chart}
      alt="Workload by member"
    />
  );
}
