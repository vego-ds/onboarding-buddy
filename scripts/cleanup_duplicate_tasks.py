import sys
from collections import defaultdict

from database.db import get_connection


def cleanup_duplicate_tasks(employee_id: str):
    query = """
    SELECT *
    FROM onboarding_tasks
    WHERE employee_id = ?
    ORDER BY created_at ASC
    """

    with get_connection() as connection:
        tasks = connection.execute(query, (employee_id,)).fetchall()
        tasks = [dict(task) for task in tasks]

        grouped_tasks = defaultdict(list)

        for task in tasks:
            grouped_tasks[task["task_name"]].append(task)

        task_ids_to_delete = []

        for task_name, duplicate_group in grouped_tasks.items():
            keep_first_task = duplicate_group[0]
            duplicate_tasks = duplicate_group[1:]

            for duplicate_task in duplicate_tasks:
                task_ids_to_delete.append(duplicate_task["task_id"])

            print(f"Keeping: {keep_first_task['task_name']} -> {keep_first_task['task_id']}")

        if not task_ids_to_delete:
            print("No duplicate tasks found.")
            return

        placeholders = ",".join(["?"] * len(task_ids_to_delete))

        delete_query = f"""
        DELETE FROM onboarding_tasks
        WHERE task_id IN ({placeholders})
        """

        connection.execute(delete_query, task_ids_to_delete)
        connection.commit()

        print(f"Deleted {len(task_ids_to_delete)} duplicate tasks.")
        print(f"Employee {employee_id} now has {len(grouped_tasks)} unique tasks.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.cleanup_duplicate_tasks EMPLOYEE_ID")
    else:
        cleanup_duplicate_tasks(sys.argv[1])
