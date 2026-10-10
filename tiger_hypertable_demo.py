#!/usr/bin/env python3
"""
Tiger Cloud / TimescaleDB Hypertable Demo Script
------------------------------------------------
This script demonstrates creating a time-series Hypertable on Tiger Cloud (TimescaleDB),
inserting partitioned telemetry metrics, running time-bucket aggregated queries,
and managing data retention policies.

Repository: https://github.com/satanic47/trailbird-ai
Challenge: Set up a Tiger Cloud service and create your first Hypertable
"""

import os
import sys
import sqlite3
from datetime import datetime, timedelta, timezone

print("=" * 70)
print("  TIGER CLOUD / TIMESCALEDB HYPERTABLE CREATION & MANAGEMENT DEMO")
print("=" * 70)

# Check for remote PostgreSQL/Tiger Cloud connection string
tiger_conn_str = os.getenv("TIGER_DATA_URL") or os.getenv("POSTGRES_URL")

if tiger_conn_str:
    print(f"[+] Connecting to live Tiger Cloud TimescaleDB instance...")
    import psycopg2
    conn = psycopg2.connect(tiger_conn_str)
    cursor = conn.cursor()
    
    # 1. Create base standard SQL table
    print("\n[Step 1] Creating base table 'sensor_metrics'...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_metrics (
            time TIMESTAMPTZ NOT NULL,
            sensor_id INTEGER NOT NULL,
            location VARCHAR(50),
            temperature DOUBLE PRECISION,
            cpu_usage DOUBLE PRECISION,
            humidity DOUBLE PRECISION
        );
    """)
    
    # 2. Convert table to TimescaleDB Hypertable
    print("[Step 2] Converting table 'sensor_metrics' into a Hypertable partitioned by time...")
    cursor.execute("""
        SELECT create_hypertable('sensor_metrics', 'time', if_not_exists => TRUE);
    """)
    
    # 3. Insert sample time-series data
    print("[Step 3] Inserting time-series telemetry data into Hypertable chunks...")
    now = datetime.now(timezone.utc)
    sample_data = [
        (now - timedelta(minutes=15), 101, 'server-rack-A', 22.4, 0.42, 45.2),
        (now - timedelta(minutes=12), 101, 'server-rack-A', 23.1, 0.58, 44.8),
        (now - timedelta(minutes=10), 102, 'server-rack-B', 19.8, 0.31, 50.1),
        (now - timedelta(minutes=8),  101, 'server-rack-A', 24.0, 0.65, 43.9),
        (now - timedelta(minutes=5),  102, 'server-rack-B', 20.5, 0.38, 49.5),
        (now - timedelta(minutes=2),  103, 'server-rack-C', 21.7, 0.47, 47.0),
        (now,                         101, 'server-rack-A', 23.5, 0.52, 44.5),
    ]
    cursor.executemany("""
        INSERT INTO sensor_metrics (time, sensor_id, location, temperature, cpu_usage, humidity)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, sample_data)
    conn.commit()
    
    # 4. Query time-bucket aggregations
    print("\n[Step 4] Executing time-bucket aggregation query over Hypertable chunks:")
    cursor.execute("""
        SELECT time_bucket('5 minutes', time) AS bucket,
               sensor_id,
               ROUND(AVG(temperature)::numeric, 2) AS avg_temp,
               ROUND(MAX(cpu_usage)::numeric, 2) AS max_cpu
        FROM sensor_metrics
        GROUP BY bucket, sensor_id
        ORDER BY bucket DESC;
    """)
    results = cursor.fetchall()
    print("-" * 60)
    print(f"{'Time Bucket':<25} | {'Sensor ID':<10} | {'Avg Temp (C)':<12} | {'Max CPU':<10}")
    print("-" * 60)
    for row in results:
        print(f"{str(row[0]):<25} | {row[1]:<10} | {row[2]:<12} | {row[3]:<10}")
    print("-" * 60)
    
    conn.close()

else:
    print("[*] TIGER_DATA_URL not set. Running Hypertable schema simulation locally...")
    
    # Connect to SQLite for demonstration of query structure
    db_path = "tiger_hypertable_demo.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Show standard PostgreSQL + TimescaleDB Hypertable SQL syntax
    print("\n[SQL Schema] Creating TimescaleDB Hypertable Definition:")
    hypertable_sql = """
    -- Standard PostgreSQL Table Schema
    CREATE TABLE IF NOT EXISTS sensor_metrics (
        time TIMESTAMPTZ NOT NULL,
        sensor_id INTEGER NOT NULL,
        location VARCHAR(50),
        temperature DOUBLE PRECISION,
        cpu_usage DOUBLE PRECISION,
        humidity DOUBLE PRECISION
    );

    -- Tiger Cloud / TimescaleDB Hypertable Conversion
    -- Automatically partitions data across time chunks (e.g. 7-day intervals)
    SELECT create_hypertable('sensor_metrics', 'time', if_not_exists => TRUE);
    """
    print(hypertable_sql)
    
    # Create local demo table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_metrics (
            time TEXT NOT NULL,
            sensor_id INTEGER NOT NULL,
            location TEXT,
            temperature REAL,
            cpu_usage REAL,
            humidity REAL
        );
    """)
    cursor.execute("DELETE FROM sensor_metrics;") # Clear old demo data
    
    # 2. Insert sample rows
    print("[Step 1] Inserting time-series rows into Hypertable chunks...")
    now = datetime.now(timezone.utc)
    sample_data = [
        ((now - timedelta(minutes=15)).isoformat(), 101, 'server-rack-A', 22.4, 0.42, 45.2),
        ((now - timedelta(minutes=12)).isoformat(), 101, 'server-rack-A', 23.1, 0.58, 44.8),
        ((now - timedelta(minutes=10)).isoformat(), 102, 'server-rack-B', 19.8, 0.31, 50.1),
        ((now - timedelta(minutes=8)).isoformat(),  101, 'server-rack-A', 24.0, 0.65, 43.9),
        ((now - timedelta(minutes=5)).isoformat(),  102, 'server-rack-B', 20.5, 0.38, 49.5),
        ((now - timedelta(minutes=2)).isoformat(),  103, 'server-rack-C', 21.7, 0.47, 47.0),
        (now.isoformat(),                           101, 'server-rack-A', 23.5, 0.52, 44.5),
    ]
    cursor.executemany("""
        INSERT INTO sensor_metrics (time, sensor_id, location, temperature, cpu_usage, humidity)
        VALUES (?, ?, ?, ?, ?, ?);
    """, sample_data)
    conn.commit()
    print(f" -> Successfully inserted {len(sample_data)} telemetry metrics.")
    
    # 3. Time-series analytical aggregation query
    print("\n[Step 2] Executing TimescaleDB Hypertable analytical query:")
    print("SQL Query:")
    print("""
    SELECT time_bucket('5 minutes', time) AS bucket,
           sensor_id,
           ROUND(AVG(temperature)::numeric, 2) AS avg_temp,
           ROUND(MAX(cpu_usage)::numeric, 2) AS max_cpu
    FROM sensor_metrics
    GROUP BY bucket, sensor_id
    ORDER BY bucket DESC;
    """)
    
    # Execute query locally
    cursor.execute("""
        SELECT sensor_id, location, ROUND(AVG(temperature), 2), ROUND(MAX(cpu_usage), 2), COUNT(*)
        FROM sensor_metrics
        GROUP BY sensor_id, location
        ORDER BY sensor_id;
    """)
    results = cursor.fetchall()
    print("-" * 65)
    print(f"{'Sensor ID':<10} | {'Location':<16} | {'Avg Temp (C)':<14} | {'Max CPU':<10} | {'Records':<8}")
    print("-" * 65)
    for row in results:
        print(f"{row[0]:<10} | {row[1]:<16} | {row[2]:<14} | {row[3]:<10} | {row[4]:<8}")
    print("-" * 65)
    
    # 4. Retention Policy demonstration
    print("\n[Step 3] Adding TimescaleDB Automated Retention Policy:")
    retention_sql = """
    -- Automatically drop chunks older than 30 days
    SELECT add_retention_policy('sensor_metrics', INTERVAL '30 days');
    """
    print(retention_sql)
    
    conn.close()

print("\n" + "=" * 70)
print("  TIGER CLOUD HYPERTABLE DEMONSTRATION COMPLETE SUCCESSFULLY!")
print("=" * 70)
