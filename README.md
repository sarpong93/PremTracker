# PremTracker

PremTracker is a project designed to generate a structured JSON output that will integrate with a web application currently in development. The goal of this app is to track and visualize the performance of Premier League (PL) teams throughout the 2024/25 season and beyond.

This initial version focuses on analyzing team statistics and assigning playing styles based on quantifiable performance metrics. The data was collected through web scraping from reputable football analytics sources, including FBref and others. Once gathered, the data underwent a custom-built ETL (Extract, Transform, Load) pipeline that ensured cleanliness, consistency, and readiness for analysis and visualization.

I have successfully utilized Apache Airflow to automate the process of updating the JSON file to GitHub on a weekly basis. By creating a custom DAG (Directed Acyclic Graph), I set up tasks to run a Python script that collects and processes data, then automatically commits and pushes the updated file to a specified GitHub repository. The DAG is scheduled to execute every Thursday, ensuring that the latest data is always reflected in the repository. 

PremTracker has been an exciting and rewarding project, and this version lays the groundwork for future enhancements. I plan to expand its capabilities with deeper insights, more nuanced metrics, and additional data sources before the new season kicks off.
