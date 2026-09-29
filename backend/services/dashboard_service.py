import base64
from io import BytesIO
from datetime import datetime

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np
import pandas as pd

from database import get_connection


# =========================================================
# LOAD TASKS
# =========================================================

def load_tasks():
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)  # yo code le chai sql excute garna help garcha
        cursor.execute("""
            SELECT
                t.id,
                t.title,
                t.description,
                t.status,
                t.priority,
                t.due_date,
                t.created_at,
                t.is_completed,
                COALESCE(
                    GROUP_CONCAT(DISTINCT u.name SEPARATOR ', '),
                    'Unassigned'
                ) AS employee_name
            FROM tasks t
            LEFT JOIN task_assignees ta ON ta.task_id = t.id
            LEFT JOIN users u ON u.id = ta.user_id
            GROUP BY
                t.id, t.title, t.description, t.status,
                t.priority, t.due_date, t.created_at, t.is_completed
        """)

        rows = cursor.fetchall()
        cursor.close()

    finally:
        connection.close()

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    # -----------------------------------------------------
    # Safe default columns
    # -----------------------------------------------------

    if "id" not in df.columns:
        df["id"] = range(1, len(df) + 1)

    if "title" not in df.columns:
        df["title"] = "Untitled Task"

    if "description" not in df.columns:
        df["description"] = ""

    if "employee_name" not in df.columns:
        df["employee_name"] = "Unassigned"

    if "status" not in df.columns:
        df["status"] = "backlog"

    if "priority" not in df.columns:
        df["priority"] = "medium"

    if "due_date" not in df.columns:
        df["due_date"] = pd.NaT

    if "created_at" not in df.columns:
        df["created_at"] = pd.NaT

    if "is_completed" not in df.columns:
        df["is_completed"] = False

    # -----------------------------------------------------
    # Clean employee names
    # -----------------------------------------------------

    df["employee_name"] = (
        df["employee_name"]
        .fillna("Unassigned")
        .astype(str)
        .str.strip()
        .replace("", "Unassigned")
    )

    # -----------------------------------------------------
    # Clean status
    # Your DB enum is: backlog, in_progress, review, done
    # -----------------------------------------------------

    df["status"] = (
        df["status"]
        .fillna("backlog")
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )

    # -----------------------------------------------------
    # Clean priority
    # -----------------------------------------------------

    df["priority"] = (
        df["priority"]
        .fillna("medium")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # -----------------------------------------------------
    # Convert dates
    # -----------------------------------------------------

    for column in ["due_date", "created_at"]:
        df[column] = pd.to_datetime(
            df[column],
            errors="coerce"
        )

    # -----------------------------------------------------
    # Completed flag
    # tasks.is_completed already exists in the DB — use it
    # directly instead of guessing from the status string.
    # -----------------------------------------------------

    df["is_completed"] = (
        df["is_completed"]
        .fillna(0)
        .astype(bool)
    )

    return df


# =========================================================
# LOAD EMPLOYEE WORKLOAD (ONE ROW PER TASK PER ASSIGNEE)
# =========================================================

def load_employee_workload():
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                u.name AS employee_name,
                t.id AS task_id,
                t.is_completed
            FROM task_assignees ta
            JOIN users u ON u.id = ta.user_id
            JOIN tasks t ON t.id = ta.task_id
        """)

        rows = cursor.fetchall()
        cursor.close()

    finally:
        connection.close()

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    df["is_completed"] = (
        df["is_completed"]
        .fillna(0)
        .astype(bool)
    )

    return df


def build_employees_summary(workload_df):
    """Numeric employee summary (name, assigned, completed, remaining) used
    both for the JSON payload and as the source data for the workload chart."""

    if workload_df.empty:
        return pd.DataFrame(columns=["name", "assigned", "completed", "remaining"])

    employees = (
        workload_df.groupby("employee_name")
        .agg(
            assigned=("task_id", "count"),
            completed=("is_completed", "sum")
        )
        .reset_index()
    )

    employees["completed"] = employees["completed"].astype(int)
    employees["remaining"] = employees["assigned"] - employees["completed"]

    employees = employees.rename(columns={"employee_name": "name"})

    return employees


# =========================================================
# MATPLOTLIB -> BASE64
# =========================================================

def chart_to_base64(fig):
    """Render a matplotlib Figure to a Base64 PNG data URL and close it,
    so figures never pile up in memory across requests."""

    buffer = BytesIO()

    fig.savefig(
        buffer,
        format="png",
        dpi=140,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )

    plt.close(fig)

    buffer.seek(0)

    return (
        "data:image/png;base64,"
        + base64.b64encode(buffer.read()).decode("utf-8")
    )


# =========================================================
# SHARED CHART STYLE
# =========================================================

FIG_FACE = "#0d2744"
AXES_FACE = "#0d2744"
TEXT_COLOR = "#e7f0fa"
GRID_COLOR = "#28516f"

STATUS_ORDER = ["Backlog", "In Progress", "Review", "Done"]
STATUS_COLORS = {
    "Backlog": "#28b8e6",
    "In Progress": "#b875ea",
    "Review": "#43d7b1",
    "Done": "#dce7f2",
}

PRIORITY_ORDER = ["Urgent", "High", "Medium", "Low"]
PRIORITY_COLORS = {
    "Urgent": "#ff626c",
    "High": "#f4c943",
    "Medium": "#28c3df",
    "Low": "#8199b2",
}


def _apply_dark_theme():
    sns.set_theme(style="darkgrid")
    plt.rcParams.update({
        "figure.facecolor": FIG_FACE,
        "axes.facecolor": AXES_FACE,
        "axes.edgecolor": GRID_COLOR,
        "axes.labelcolor": TEXT_COLOR,
        "text.color": TEXT_COLOR,
        "xtick.color": TEXT_COLOR,
        "ytick.color": TEXT_COLOR,
        "grid.color": GRID_COLOR,
        "grid.alpha": 0.35,
        "font.size": 11,
    })


# =========================================================
# STATUS CHART — seaborn vertical bar chart
# =========================================================

def make_status_chart(df):
    if df.empty:
        return None

    _apply_dark_theme()

    counts = (
        df["status"]
        .str.replace("_", " ", regex=False)
        .str.title()
        .value_counts()
    )

    counts = counts.reindex([s for s in STATUS_ORDER if s in counts.index] +
                             [s for s in counts.index if s not in STATUS_ORDER])

    fig, ax = plt.subplots(figsize=(6.5, 4.2))

    palette = [STATUS_COLORS.get(label, "#28b8e6") for label in counts.index]

    sns.barplot(
        x=counts.index,
        y=counts.values,
        hue=counts.index,
        palette=palette,
        legend=False,
        ax=ax,
        edgecolor="none",
    )

    for i, value in enumerate(counts.values):
        ax.text(i, value + max(counts.values) * 0.02, str(int(value)),
                ha="center", va="bottom", fontsize=10, fontweight="bold", color=TEXT_COLOR)

    ax.set_title("Tasks by Status", fontsize=14, fontweight="bold", color=TEXT_COLOR, pad=14)
    ax.set_xlabel("")
    ax.set_ylabel("Number of Tasks")
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax.tick_params(axis="x", rotation=0)
    sns.despine(ax=ax, left=True, bottom=True)

    fig.tight_layout()

    return chart_to_base64(fig)


# =========================================================
# PRIORITY CHART — matplotlib donut chart
# =========================================================

def make_priority_chart(df):
    if df.empty:
        return None

    _apply_dark_theme()

    counts = df["priority"].str.title().value_counts()
    counts = counts.reindex([p for p in PRIORITY_ORDER if p in counts.index] +
                             [p for p in counts.index if p not in PRIORITY_ORDER])

    colors = [PRIORITY_COLORS.get(label, "#28c3df") for label in counts.index]

    fig, ax = plt.subplots(figsize=(6, 5.2))

    wedges, _texts, autotexts = ax.pie(
        counts.values,
        colors=colors,
        autopct="%1.0f%%",
        pctdistance=0.8,
        startangle=90,
        wedgeprops={"width": 0.4, "edgecolor": FIG_FACE, "linewidth": 2},
    )

    for text in autotexts:
        text.set_color(TEXT_COLOR)
        text.set_fontsize(10)
        text.set_fontweight("bold")

    ax.text(0, 0, f"{int(counts.sum())}\nTasks", ha="center", va="center",
            fontsize=13, fontweight="bold", color=TEXT_COLOR)

    ax.legend(
        wedges,
        [f"{label} ({count})" for label, count in zip(counts.index, counts.values)],
        loc="upper center",
        bbox_to_anchor=(0.5, -0.02),
        ncol=2,
        frameon=False,
        labelcolor=TEXT_COLOR,
        fontsize=9,
    )

    ax.set_title("Tasks by Priority", fontsize=14, fontweight="bold", color=TEXT_COLOR, pad=14)
    ax.set_ylabel("")
    ax.axis("equal")

    fig.tight_layout()

    return chart_to_base64(fig)


# =========================================================
# WORKLOAD CHART — seaborn-styled horizontal stacked bar
# =========================================================

def make_workload_chart(employees_df):
    if employees_df.empty:
        return None

    _apply_dark_theme()

    rows = employees_df.sort_values("assigned", ascending=True).tail(12)

    fig, ax = plt.subplots(figsize=(7.5, max(3.5, 0.55 * len(rows) + 1.5)))

    y_pos = np.arange(len(rows))

    ax.barh(y_pos, rows["completed"], color="#4bdcb0", label="Completed", edgecolor="none")
    ax.barh(y_pos, rows["remaining"], left=rows["completed"], color="#20a9ff",
            label="Remaining", edgecolor="none")

    for i, (assigned, completed) in enumerate(zip(rows["assigned"], rows["completed"])):
        ax.text(assigned + max(rows["assigned"]) * 0.02, i, f"{assigned} assigned",
                va="center", fontsize=9, color=TEXT_COLOR)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(rows["name"])
    ax.set_xlabel("Tasks")
    ax.set_ylabel("")
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))

    ax.set_title("Workload by Employee", fontsize=14, fontweight="bold", color=TEXT_COLOR, pad=14)
    ax.legend(loc="lower right", frameon=False, labelcolor=TEXT_COLOR, fontsize=9)
    sns.despine(ax=ax, left=True, bottom=True)

    fig.tight_layout()

    return chart_to_base64(fig)


# =========================================================
# TIMELINE CHART — matplotlib line chart with date formatting
# =========================================================

def make_timeline_chart(df):
    if df.empty:
        return None

    _apply_dark_theme()

    dated = df.dropna(subset=["due_date"])

    fig, ax = plt.subplots(figsize=(8, 4.2))

    if dated.empty:
        ax.text(0.5, 0.5, "No due dates available", ha="center", va="center",
                fontsize=12, color="#7891ac", transform=ax.transAxes)
        ax.set_xticks([])
        ax.set_yticks([])
    else:
        timeline = (
            dated.groupby(dated["due_date"].dt.date)
            .size()
            .sort_index()
        )

        x_labels = [d.strftime("%b %d") for d in timeline.index]
        x_pos = np.arange(len(timeline))

        ax.plot(x_pos, timeline.values, marker="o", color="#32c7e5",
                linewidth=2.5, markersize=6, markerfacecolor="#0b2138",
                markeredgewidth=2, markeredgecolor="#32c7e5")
        ax.fill_between(x_pos, timeline.values, color="#32c7e5", alpha=0.12)

        ax.set_xticks(x_pos)
        ax.set_xticklabels(x_labels, rotation=30, ha="right")
        ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        ax.set_ylabel("Tasks Due")

    ax.set_title("Tasks by Due Date", fontsize=14, fontweight="bold", color=TEXT_COLOR, pad=14)
    ax.set_xlabel("")
    sns.despine(ax=ax, left=True, bottom=True)

    fig.tight_layout()

    return chart_to_base64(fig)


# =========================================================
# CREATE ALL CHARTS
# =========================================================

def make_charts(df, employees_df):
    return {
        "status": make_status_chart(df),
        "priority": make_priority_chart(df),
        "workload": make_workload_chart(employees_df),
        "timeline": make_timeline_chart(df),
    }


# =========================================================
# DASHBOARD
# =========================================================

def get_dashboard():

    df = load_tasks()

    # =====================================================
    # EMPTY DATABASE
    # =====================================================

    if df.empty:

        return {
            "summary": {
                "total_tasks": 0,
                "completed": 0,
                "backlog": 0,
                "in_progress": 0,
                "review": 0,
                "overdue": 0,
                "completion_percentage": 0
            },

            "status": [],

            "priority": [],

            "employees": [],

            "tasks": [],

            "recent_activity": [],

            "charts": {
                "status": None,
                "priority": None,
                "workload": None,
                "timeline": None
            }
        }

    # =====================================================
    # SUMMARY
    # =====================================================

    total_tasks = len(df)

    completed = int(
        df["is_completed"].sum()
    )

    backlog = int(
        (df["status"] == "backlog").sum()
    )

    in_progress = int(
        (df["status"] == "in_progress").sum()
    )

    review = int(
        (df["status"] == "review").sum()
    )

    # =====================================================
    # TODAY
    # =====================================================

    today = pd.Timestamp(
        datetime.now().date()
    )

    # =====================================================
    # OVERDUE
    # =====================================================

    overdue = int(
        (
            df["due_date"].notna()
            & (df["due_date"] < today)
            & (~df["is_completed"])
        ).sum()
    )

    # =====================================================
    # COMPLETION PERCENTAGE
    # NUMPY
    # =====================================================

    completion_percentage = int(
        np.divide(
            completed * 100,
            total_tasks,
            out=np.array(0.0),
            where=total_tasks != 0
        )
    )

    # =====================================================
    # STATUS
    # =====================================================

    status = (
        df["status"]
        .str.replace("_", " ", regex=False)
        .str.title()
        .value_counts()
        .reset_index()
    )

    status.columns = [
        "status",
        "count"
    ]

    # =====================================================
    # PRIORITY
    # =====================================================

    priority = (
        df["priority"]
        .str.title()
        .value_counts()
        .reset_index()
    )

    priority.columns = [
        "priority",
        "count"
    ]

    # =====================================================
    # EMPLOYEE WORKLOAD
    # =====================================================

    workload_df = load_employee_workload()
    employees_numeric = build_employees_summary(workload_df)

    # =====================================================
    # CHARTS
    # Built from the numeric data before it gets cast to
    # JSON-safe objects below.
    # =====================================================

    charts = make_charts(df, employees_numeric)

    employees = employees_numeric.copy()

    # =====================================================
    # TASK TABLE
    # =====================================================

    tasks = df.copy()

    tasks["assignee_name"] = (
        tasks["employee_name"]
    )

    # Convert dates into JSON-safe strings

    for column in [
        "due_date",
        "created_at"
    ]:

        tasks[column] = (
            tasks[column]
            .dt.strftime("%Y-%m-%d")
            .where(
                tasks[column].notna(),
                None
            )
        )

    # =====================================================
    # TASK COLUMNS
    # =====================================================

    task_columns = [
        "id",
        "title",
        "description",
        "assignee_name",
        "status",
        "priority",
        "due_date",
        "created_at"
    ]

    task_columns = [
        column
        for column in task_columns
        if column in tasks.columns
    ]

    tasks = tasks[
        task_columns
    ]

    # =====================================================
    # RECENT ACTIVITY
    # =====================================================

    recent = (
        df.dropna(
            subset=["created_at"]
        )
        .sort_values(
            "created_at",
            ascending=False
        )
        .head(10)
        .copy()
    )

    recent_activity = []

    for _, row in recent.iterrows():

        recent_activity.append(
            {
                "user_name": str(
                    row["employee_name"]
                ),

                "task_title": str(
                    row["title"]
                ),

                "created_at": (
                    row["created_at"]
                    .strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )
            }
        )

    # =====================================================
    # CONVERT DATA TO JSON SAFE VALUES
    # =====================================================

    tasks = (
        tasks.astype(object)
        .where(
            tasks.notna(),
            None
        )
    )

    employees = (
        employees.astype(object)
        .where(
            employees.notna(),
            None
        )
    )

    status = (
        status.astype(object)
        .where(
            status.notna(),
            None
        )
    )

    priority = (
        priority.astype(object)
        .where(
            priority.notna(),
            None
        )
    )

    # =====================================================
    # RETURN EVERYTHING
    # =====================================================

    return {

        "summary": {

            "total_tasks": int(
                total_tasks
            ),

            "completed": int(
                completed
            ),

            "backlog": int(
                backlog
            ),

            "in_progress": int(
                in_progress
            ),

            "review": int(
                review
            ),

            "overdue": int(
                overdue
            ),

            "completion_percentage": int(
                completion_percentage
            )
        },

        "status": status.to_dict(
            orient="records"
        ),

        "priority": priority.to_dict(
            orient="records"
        ),

        "employees": employees.to_dict(
            orient="records"
        ),

        "tasks": tasks.to_dict(
            orient="records"
        ),

        "recent_activity": recent_activity,

        "charts": charts
    }
