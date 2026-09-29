import ChartCard from "./ChartCard";

export default function TimelineChart({ chart }) {
  return (
    <ChartCard
      title="Tasks by due date"
      subtitle="Track how many tasks are scheduled for each upcoming deadline."
      chart={chart}
      alt="Tasks by due date"
    />
  );
}
