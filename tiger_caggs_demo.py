#!/usr/bin/env python3
"""
Tiger Cloud / TimescaleDB Continuous Aggregates (CAGGs) Demo
------------------------------------------------------------
This script demonstrates creating Continuous Aggregates (CAGGs) on a TimescaleDB Hypertable
to compute real-time hourly metrics (AVG temperature, MAX CPU, COUNT readings) with automated
background refresh policies.

Repository: https://github.com/satanic47/trailbird-ai
Challenge: Accelerate Dashboards with Continuous Aggregates
"""

import os
import sys
import sqlite3
from datetime import datetime, timedelta, timezone

print("=" * 75)
print("  TIGER CLOUD CONTINUOUS AGGREGATES (CAGGs) & TIME BUCKETS DEMO")
print("=" * 75)

# Check for live PostgreSQL / Tiger Cloud connection
tiger_conn_str = os.getenv("TIGER_DATA_URL") or os.getenv("POSTGRES_URL")

if tiger_conn_str:
    print("[+] Connecting to live Tiger Cloud TimescaleDB instance...")
    import psycopg2
    conn = psycopg2.connect(tiger_conn_str)
    cursor = conn.cursor()
    
    # 1. Base table & Hypertable setup
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_metrics (
            time TIMESTAMPTZ NOT NULL,
            sensor_id INTEGER NOT NULL,
            location VARCHAR(50),
            temperature DOUBLE PRECISION,
            cpu_usage DOUBLE PRECISION
        );
        SELECT create_hypertable('sensor_metrics', 'time', if_not_exists => TRUE);
    """)
    
    # 2. Create Continuous Aggregate (CAGG)
    print("\n[Step 1] Creating Continuous Aggregate Materialized View 'hourly_sensor_summary'...")
    cursor.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS hourly_sensor_summary
        WITH (timescaledb.continuous) AS
        SELECT time_bucket('1 hour', time) AS bucket,
               sensor_id,
               AVG(temperature) AS avg_temp,
               MAX(cpu_usage) AS max_cpu,
               COUNT(*) AS num_readings
        FROM sensor_metrics
        GROUP BY bucket, sensor_id;
    """)
    
    # 3. Add Continuous Aggregate Refresh Policy
    print("[Step 2] Configuring Automated Continuous Aggregate Refresh Policy...")
    cursor.execute("""
        SELECT add_continuous_aggregate_policy('hourly_sensor_summary',
            start_offset => INTERVAL '1 month',
            end_offset => INTERVAL '1 hour',
            schedule_interval => INTERVAL '1 hour',
            if_not_exists => TRUE);
    """)
    conn.commit()
    
    # 4. Query Continuous Aggregate
    print("\n[Step 3] Querying Continuous Aggregate View:")
    cursor.execute("SELECT * FROM hourly_sensor_summary ORDER BY bucket DESC;")
    results = cursor.fetchall()
    print("-" * 65)
    print(f"{'Bucket Hour':<25} | {'Sensor ID':<10} | {'Avg Temp (C)':<12} | {'Max CPU':<10}")
    print("-" * 65)
    for row in results:
        print(f"{str(row[0]):<25} | {row[1]:<10} | {row[2]:<12} | {row[3]:<10}")
    print("-" * 65)
    conn.close()

else:
    print("[*] TIGER_DATA_URL not set. Demonstrating CAGG SQL schema & executing local view simulation...")
    
    print("\n[TimescaleDB Continuous Aggregate SQL Schema]")
    cagg_sql = """
    -- 1. Create Continuous Aggregate (CAGG) Materialized View
    -- Pre-computes hourly sensor averages and peak CPU usage in background
    CREATE MATERIALIZED VIEW hourly_sensor_summary
    WITH (timescaledb.continuous) AS
    SELECT time_bucket('1 hour', time) AS bucket,
           sensor_id,
           AVG(temperature) AS avg_temp,
           MAX(cpu_usage) AS max_cpu,
           COUNT(*) AS num_readings
    FROM sensor_metrics
    GROUP BY bucket, sensor_id;

    -- 2. Add Continuous Aggregate Refresh Policy
    SELECT add_continuous_aggregate_policy('hourly_sensor_summary',
        start_offset => INTERVAL '1 month',
        end_offset => INTERVAL '1 hour',
        schedule_interval => INTERVAL '1 hour');

    -- 3. Fast Dashboard Query over CAGG View
    SELECT * FROM hourly_sensor_summary ORDER BY bucket DESC;
    """
    print(cagg_sql)
    
    # Execute local simulation SQLite database
    db_path = "tiger_caggs_demo.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_metrics (
            time TEXT NOT NULL,
            sensor_id INTEGER NOT NULL,
            location TEXT,
            temperature REAL,
            cpu_usage REAL
        );
    """)
    cursor.execute("DELETE FROM sensor_metrics;")
    
    now = datetime.now(timezone.utc)
    sample_rows = [
        ((now - timedelta(hours=3)).isoformat(), 101, 'server-rack-A', 22.4, 0.42),
        ((now - timedelta(hours=2)).isoformat(), 101, 'server-rack-A', 23.1, 0.58),
        ((now - timedelta(hours=2)).isoformat(), 102, 'server-rack-B', 19.8, 0.31),
        ((now - timedelta(hours=1)).isoformat(), 101, 'server-rack-A', 24.0, 0.65),
        ((now - timedelta(hours=1)).isoformat(), 102, 'server-rack-B', 20.5, 0.38),
        (now.isoformat(),                        103, 'server-rack-C', 21.7, 0.47),
    ]
    cursor.executemany("""
        INSERT INTO sensor_metrics (time, sensor_id, location, temperature, cpu_usage)
        VALUES (?, ?, ?, ?, ?);
    """, sample_rows)
    conn.commit()
    
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS hourly_sensor_summary AS
        SELECT strftime('%Y-%m-%d %H:00:00', time) AS bucket,
               sensor_id,
               ROUND(AVG(temperature), 2) AS avg_temp,
               ROUND(MAX(cpu_usage), 2) AS max_cpu,
               COUNT(*) AS num_readings
        FROM sensor_metrics
        GROUP BY bucket, sensor_id;
    """)
    
    print("[Step 1] Querying simulated Continuous Aggregate View 'hourly_sensor_summary':")
    cursor.execute("SELECT bucket, sensor_id, avg_temp, max_cpu, num_readings FROM hourly_sensor_summary ORDER BY bucket DESC;")
    results = cursor.fetchall()
    
    print("-" * 75)
    print(f"{'Bucket Hour':<22} | {'Sensor ID':<10} | {'Avg Temp (C)':<12} | {'Max CPU':<10} | {'Readings':<8}")
    print("-" * 75)
    for r in results:
        print(f"{r[0]:<22} | {r[1]:<10} | {r[2]:<12} | {r[3]:<10} | {r[4]:<8}")
    print("-" * 75)
    conn.close()

print("\n" + "=" * 75)
print("  CONTINUOUS AGGREGATES DEMONSTRATION COMPLETED SUCCESSFULLY!")
print("=" * 75)
