#!/usr/bin/env python3
"""
Tiger Cloud IoT Sensor Data Simulation & Relational Metadata Query Demo
-----------------------------------------------------------------------
This script simulates a real-world IoT sensor dataset on Tiger Cloud (TimescaleDB).
It models relational metadata (`devices` table: model, device_type, firmware, location)
and time-series metrics (`sensor_readings` hypertable: battery, temp, humidity, pressure).

Repository: https://github.com/satanic47/trailbird-ai
Challenge: Simulate an IoT Sensor Dataset on Tiger Cloud
"""

import os
import sys
import sqlite3
from datetime import datetime, timedelta, timezone

print("=" * 75)
print("  TIGER CLOUD IOT SENSOR DATASET SIMULATION & HYPERTABLE DEMO")
print("=" * 75)

# Check for live PostgreSQL / Tiger Cloud connection
tiger_conn_str = os.getenv("TIGER_DATA_URL") or os.getenv("POSTGRES_URL")

if tiger_conn_str:
    print("[+] Connecting to live Tiger Cloud TimescaleDB instance...")
    import psycopg2
    conn = psycopg2.connect(tiger_conn_str)
    cursor = conn.cursor()
    
    # 1. Relational Metadata Table: devices
    print("\n[Step 1] Creating relational metadata table 'devices'...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            device_id VARCHAR(50) PRIMARY KEY,
            device_type VARCHAR(50) NOT NULL,
            model VARCHAR(50),
            firmware_version VARCHAR(20),
            location VARCHAR(100),
            installed_at TIMESTAMPTZ DEFAULT NOW()
        );
    """)
    
    # 2. Time-Series Hypertable: sensor_readings
    print("[Step 2] Creating time-series Hypertable 'sensor_readings'...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_readings (
            time TIMESTAMPTZ NOT NULL,
            device_id VARCHAR(50) NOT NULL,
            battery_level DOUBLE PRECISION,
            temperature DOUBLE PRECISION,
            humidity DOUBLE PRECISION,
            pressure_hpa DOUBLE PRECISION
        );
        SELECT create_hypertable('sensor_readings', 'time', if_not_exists => TRUE);
    """)
    
    # Insert devices metadata
    devices_data = [
        ('iot-bulb-01', 'Smart Light Bulb', 'Lumina-Pro-X', 'v2.4.1', 'Building A - Room 101'),
        ('iot-well-02', 'Industrial Well Sensor', 'HydroSense-9000', 'v1.8.0', 'Field Site 4 - Well B'),
        ('iot-hvac-03', 'HVAC Controller', 'ClimateMaster-3000', 'v3.1.2', 'Building B - Rooftop'),
    ]
    cursor.executemany("""
        INSERT INTO devices (device_id, device_type, model, firmware_version, location)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (device_id) DO NOTHING;
    """, devices_data)
    
    # Insert time-series readings
    now = datetime.now(timezone.utc)
    readings = [
        (now - timedelta(minutes=30), 'iot-bulb-01', 98.5, 21.2, 45.0, 1013.25),
        (now - timedelta(minutes=20), 'iot-well-02', 84.0, 15.8, 72.4, 1020.10),
        (now - timedelta(minutes=15), 'iot-hvac-03', 92.1, 23.5, 48.2, 1012.80),
        (now - timedelta(minutes=10), 'iot-bulb-01', 98.0, 21.6, 44.8, 1013.30),
        (now - timedelta(minutes=5),  'iot-well-02', 83.5, 16.1, 71.9, 1020.05),
        (now,                         'iot-hvac-03', 91.8, 23.9, 47.9, 1012.75),
    ]
    cursor.executemany("""
        INSERT INTO sensor_readings (time, device_id, battery_level, temperature, humidity, pressure_hpa)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, readings)
    conn.commit()
    
    # 3. Relational Join + Time-Bucket Query
    print("\n[Step 3] Running relational join query (devices JOIN sensor_readings):")
    cursor.execute("""
        SELECT time_bucket('10 minutes', r.time) AS bucket,
               d.device_id,
               d.device_type,
               d.location,
               ROUND(AVG(r.temperature)::numeric, 2) AS avg_temp,
               ROUND(AVG(r.battery_level)::numeric, 1) AS avg_battery
        FROM sensor_readings r
        JOIN devices d ON r.device_id = d.device_id
        GROUP BY bucket, d.device_id, d.device_type, d.location
        ORDER BY bucket DESC;
    """)
    results = cursor.fetchall()
    print("-" * 80)
    print(f"{'Time Bucket':<22} | {'Device ID':<12} | {'Device Type':<22} | {'Avg Temp':<10} | {'Battery %':<8}")
    print("-" * 80)
    for r in results:
        print(f"{str(r[0]):<22} | {r[1]:<12} | {r[2]:<22} | {r[4]:<10} | {r[5]:<8}")
    print("-" * 80)
    conn.close()

else:
    print("[*] TIGER_DATA_URL not set. Demonstrating IoT SQL Schema & executing local simulation...")
    
    iot_sql = """
    -- 1. Relational Device Metadata Table
    CREATE TABLE IF NOT EXISTS devices (
        device_id VARCHAR(50) PRIMARY KEY,
        device_type VARCHAR(50) NOT NULL,
        model VARCHAR(50),
        firmware_version VARCHAR(20),
        location VARCHAR(100),
        installed_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- 2. Time-Series Hypertable for IoT Telemetry Readings
    CREATE TABLE IF NOT EXISTS sensor_readings (
        time TIMESTAMPTZ NOT NULL,
        device_id VARCHAR(50) NOT NULL REFERENCES devices(device_id),
        battery_level DOUBLE PRECISION,
        temperature DOUBLE PRECISION,
        humidity DOUBLE PRECISION,
        pressure_hpa DOUBLE PRECISION
    );
    SELECT create_hypertable('sensor_readings', 'time', if_not_exists => TRUE);

    -- 3. Ingest Device Metadata & Readings
    INSERT INTO devices (device_id, device_type, model, firmware_version, location) VALUES
    ('iot-bulb-01', 'Smart Light Bulb', 'Lumina-Pro-X', 'v2.4.1', 'Building A - Room 101'),
    ('iot-well-02', 'Industrial Well Sensor', 'HydroSense-9000', 'v1.8.0', 'Field Site 4 - Well B'),
    ('iot-hvac-03', 'HVAC Controller', 'ClimateMaster-3000', 'v3.1.2', 'Building B - Rooftop');

    -- 4. Analytical Join Query
    SELECT time_bucket('10 minutes', r.time) AS bucket,
           d.device_id,
           d.device_type,
           d.location,
           ROUND(AVG(r.temperature)::numeric, 2) AS avg_temp,
           ROUND(AVG(r.battery_level)::numeric, 1) AS avg_battery
    FROM sensor_readings r
    JOIN devices d ON r.device_id = d.device_id
    GROUP BY bucket, d.device_id, d.device_type, d.location
    ORDER BY bucket DESC;
    """
    print("\n[TimescaleDB IoT Dataset SQL Schema]")
    print(iot_sql)
    
    # Execute local simulation SQLite database
    db_path = "tiger_iot_sensor_sim.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            device_id TEXT PRIMARY KEY,
            device_type TEXT NOT NULL,
            model TEXT,
            firmware_version TEXT,
            location TEXT
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_readings (
            time TEXT NOT NULL,
            device_id TEXT NOT NULL,
            battery_level REAL,
            temperature REAL,
            humidity REAL,
            pressure_hpa REAL
        );
    """)
    cursor.execute("DELETE FROM devices;")
    cursor.execute("DELETE FROM sensor_readings;")
    
    cursor.executemany("""
        INSERT INTO devices (device_id, device_type, model, firmware_version, location)
        VALUES (?, ?, ?, ?, ?);
    """, [
        ('iot-bulb-01', 'Smart Light Bulb', 'Lumina-Pro-X', 'v2.4.1', 'Building A - Room 101'),
        ('iot-well-02', 'Industrial Well Sensor', 'HydroSense-9000', 'v1.8.0', 'Field Site 4 - Well B'),
        ('iot-hvac-03', 'HVAC Controller', 'ClimateMaster-3000', 'v3.1.2', 'Building B - Rooftop'),
    ])
    
    now = datetime.now(timezone.utc)
    readings = [
        ((now - timedelta(minutes=30)).isoformat(), 'iot-bulb-01', 98.5, 21.2, 45.0, 1013.25),
        ((now - timedelta(minutes=20)).isoformat(), 'iot-well-02', 84.0, 15.8, 72.4, 1020.10),
        ((now - timedelta(minutes=15)).isoformat(), 'iot-hvac-03', 92.1, 23.5, 48.2, 1012.80),
        ((now - timedelta(minutes=10)).isoformat(), 'iot-bulb-01', 98.0, 21.6, 44.8, 1013.30),
        ((now - timedelta(minutes=5)).isoformat(),  'iot-well-02', 83.5, 16.1, 71.9, 1020.05),
        (now.isoformat(),                         'iot-hvac-03', 91.8, 23.9, 47.9, 1012.75),
    ]
    cursor.executemany("""
        INSERT INTO sensor_readings (time, device_id, battery_level, temperature, humidity, pressure_hpa)
        VALUES (?, ?, ?, ?, ?, ?);
    """, readings)
    conn.commit()
    
    print("\n[Step 1] Executing Relational Join Query (devices JOIN sensor_readings):")
    cursor.execute("""
        SELECT d.device_id, d.device_type, d.location, ROUND(AVG(r.temperature), 2), ROUND(AVG(r.battery_level), 1), COUNT(*)
        FROM sensor_readings r
        JOIN devices d ON r.device_id = d.device_id
        GROUP BY d.device_id, d.device_type, d.location
        ORDER BY d.device_id;
    """)
    results = cursor.fetchall()
    print("-" * 80)
    print(f"{'Device ID':<12} | {'Device Type':<22} | {'Location':<24} | {'Avg Temp':<10} | {'Readings':<8}")
    print("-" * 80)
    for r in results:
        print(f"{r[0]:<12} | {r[1]:<22} | {r[2]:<24} | {r[3]:<10} | {r[5]:<8}")
    print("-" * 80)
    conn.close()

print("\n" + "=" * 75)
print("  IOT SENSOR SIMULATION & RELATIONAL QUERY COMPLETED SUCCESSFULLY!")
print("=" * 75)
