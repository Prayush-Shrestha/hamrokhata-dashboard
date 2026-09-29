import ChartCard from "./ChartCard";

export default function StatusChart({ chart }) {
  return (
    <ChartCard
      title="Tasks by status"
      subtitle="See where the team's work is right now."
      chart={chart}
      alt="Tasks by status"
    />
  );
}
