from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'PY',
    'depends_on_past': False,
    'start_date': datetime(2025, 4, 23),
    'end_date': datetime(2025, 5, 30),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'weekly_push_to_github',
    default_args=default_args,
    description='Run script weekly and push to GitHub',
    schedule_interval='0 0 * * 4',  # Every Thursday at midnight',
    catchup=False
)

run_python_script = BashOperator(
    task_id='run_team_script',
    bash_command='python3 /Users/papayaw/projects/premtracker/PremTracker.py',
    dag=dag
)

git_commit_push = BashOperator(
    task_id='push_to_github',
    bash_command="""
    cd /Users/papayaw/projects/premtracker &&
    git add team_styles.json &&
    git commit -m "Weekly update from Airflow" || echo "No changes to commit" &&
    git push 
    """,
    dag=dag
)

run_python_script >> git_commit_push