// turns "in_progress" into "In Progress"
export function formatStatus(value) {
  if (!value) return "-";
  const words = String(value).split("_");
  let result = "";
  for (let i = 0; i < words.length; i++) {
    const w = words[i];
    result += w.charAt(0).toUpperCase() + w.slice(1);
    if (i < words.length - 1) result += " ";
  }
  return result;
}

export function getStatusClass(status) {
  const v = String(status || "").toLowerCase();
  if (v === "completed" || v === "done") return "done";
  if (v === "in_progress") return "progress";
  if (v === "review") return "review";
  return "backlog";
}

export function getInitials(name) {
  if (!name) return "U";
  const parts = name.trim().split(/\s+/);
  let initials = "";
  for (let i = 0; i < parts.length && i < 2; i++) {
    initials += parts[i][0];
  }
  return initials.toUpperCase();
}
