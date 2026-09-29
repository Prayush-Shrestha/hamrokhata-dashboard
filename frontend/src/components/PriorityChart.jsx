import ChartCard from "./ChartCard";

export default function PriorityChart({ chart }) {
  return (
    <ChartCard
      title="Tasks by priority"
      subtitle="Understand what needs attention first."
      chart={chart}
      alt="Tasks by priority"
    />
  );
}
