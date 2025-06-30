
import json

# Initialize an empty list to store anomalies
anomalies = []

try:
    with open('parsed_telemetry.json', 'r') as f:
        telemetry_data = json.load(f)

    # --- Anomaly Detection Thresholds (can be adjusted based on vehicle type and sensor specs) ---
    # IMU thresholds (values typically in milli-g or centi-g for acceleration, milli-deg/s or centi-deg/s for gyro)
    # Assuming 1g = 1000 (for RAW_IMU, SCALED_IMU/SCALED_IMU2 as seen in example snippet)
    ACCEL_SPIKE_THRESHOLD_MG_CG = 2000  # 2g for SCALED_IMU (or 2000mg for RAW_IMU)
    GYRO_SPIKE_THRESHOLD_MDEGS_CDEGS = 1000 # 100 deg/s (if 10 = 1 deg/s, then 1000 = 100 deg/s)

    # Pressure thresholds (hPa)
    PRESSURE_RATE_CHANGE_THRESHOLD_HPA_PER_SEC = 50 # hPa change per second

    # Battery thresholds (mV, percentage)
    BATTERY_VOLTAGE_LOW_THRESHOLD_MV = 10000 # 10V (e.g., for a 3S battery)
    BATTERY_REMAINING_LOW_THRESHOLD_PERCENT = 20 # 20%

    # System status thresholds
    CPU_LOAD_HIGH_THRESHOLD_PERCENT = 900 # 90% (load is often scaled by 1000, so 90% is 900)

    # GPS thresholds
    GPS_EPH_HIGH_THRESHOLD_CM = 200 # 200 cm = 2.0 m HDOP
    GPS_SATS_LOW_THRESHOLD = 6 # Minimum number of satellites for a good fix

    # Vibration thresholds (m/s^2 RMS)
    VIBE_THRESHOLD_RMS_SQ = 30 # For example, sqrt(30) ~ 5.5 m/s^2 RMS, values often stored squared. ArduPilot recommends < 15 m/s^2 RMS.

    # Store previous values for change detection (e.g., for pressure, velocity)
    prev_pressure_abs = None
    prev_timestamp_pressure = None

    for entry in telemetry_data:
        data_type = entry.get('type')
        data = entry.get('data')

        if not data:
            continue

        timestamp = data.get('timestamp') # All entries in example have a timestamp

        # --- IMU Anomaly Detection (RAW_IMU, SCALED_IMU, SCALED_IMU2) ---
        if data_type in ['RAW_IMU', 'SCALED_IMU', 'SCALED_IMU2']:
            xacc = data.get('xacc')
            yacc = data.get('yacc')
            zacc = data.get('zacc')
            xgyro = data.get('xgyro')
            ygyro = data.get('ygyro')
            zgyro = data.get('zgyro')

            # Check for acceleration spikes (deviation from expected 0g for X/Y, -1g for Z)
            if xacc is not None and abs(xacc) > ACCEL_SPIKE_THRESHOLD_MG_CG:
                anomalies.append(f"[{timestamp}] {data_type}: X-acceleration spike detected ({xacc})")
            if yacc is not None and abs(yacc) > ACCEL_SPIKE_THRESHOLD_MG_CG:
                anomalies.append(f"[{timestamp}] {data_type}: Y-acceleration spike detected ({yacc})")
            # For Z-accel, normal is around -1000 (for 1g = 1000 units). Check deviation from -1g.
            if zacc is not None and abs(zacc + 1000) > ACCEL_SPIKE_THRESHOLD_MG_CG:
                anomalies.append(f"[{timestamp}] {data_type}: Z-acceleration spike detected ({zacc})")

            # Check for gyro spikes
            if xgyro is not None and abs(xgyro) > GYRO_SPIKE_THRESHOLD_MDEGS_CDEGS:
                anomalies.append(f"[{timestamp}] {data_type}: X-gyro spike detected ({xgyro})")
            if ygyro is not None and abs(ygyro) > GYRO_SPIKE_THRESHOLD_MDEGS_CDEGS:
                anomalies.append(f"[{timestamp}] {data_type}: Y-gyro spike detected ({ygyro})")
            if zgyro is not None and abs(zgyro) > GYRO_SPIKE_THRESHOLD_MDEGS_CDEGS:
                anomalies.append(f"[{timestamp}] {data_type}: Z-gyro spike detected ({zgyro})")

        # --- Pressure Anomaly Detection (SCALED_PRESSURE) ---
        if data_type == 'SCALED_PRESSURE':
            press_abs = data.get('press_abs') # hPa
            if press_abs is not None:
                if prev_pressure_abs is not None and timestamp is not None and prev_timestamp_pressure is not None:
                    time_diff = timestamp - prev_timestamp_pressure
                    if time_diff > 0: # Avoid division by zero
                        pressure_change_rate = abs(press_abs - prev_pressure_abs) / time_diff
                        if pressure_change_rate > PRESSURE_RATE_CHANGE_THRESHOLD_HPA_PER_SEC:
                            anomalies.append(f"[{timestamp}] SCALED_PRESSURE: Sudden large pressure change detected ({press_abs - prev_pressure_abs:.2f} hPa over {time_diff:.2f}s)")
                prev_pressure_abs = press_abs
                prev_timestamp_pressure = timestamp

        # --- System Status Anomaly Detection (SYS_STATUS) ---
        if data_type == 'SYS_STATUS':
            voltage_battery = data.get('voltage_battery') # mV
            battery_remaining = data.get('battery_remaining') # %
            load = data.get('load') # CPU load in % * 10 (e.g., 900 for 90%)
            errors_comm = data.get('errors_comm')
            errors_count1 = data.get('errors_count1')
            errors_count2 = data.get('errors_count2')
            errors_count3 = data.get('errors_count3')
            errors_count4 = data.get('errors_count4')

            if voltage_battery is not None and voltage_battery > 0 and voltage_battery < BATTERY_VOLTAGE_LOW_THRESHOLD_MV:
                anomalies.append(f"[{timestamp}] SYS_STATUS: Low battery voltage detected ({voltage_battery/1000.0:.2f} V)")
            if battery_remaining is not None and battery_remaining >= 0 and battery_remaining < BATTERY_REMAINING_LOW_THRESHOLD_PERCENT:
                anomalies.append(f"[{timestamp}] SYS_STATUS: Low battery remaining detected ({battery_remaining} %)")
            if load is not None and load > CPU_LOAD_HIGH_THRESHOLD_PERCENT:
                anomalies.append(f"[{timestamp}] SYS_STATUS: High CPU load detected ({load/10.0:.1f} %)")
            if errors_comm is not None and errors_comm > 0:
                anomalies.append(f"[{timestamp}] SYS_STATUS: Communication errors detected ({errors_comm} errors)")
            if errors_count1 is not None and errors_count1 > 0:
                anomalies.append(f"[{timestamp}] SYS_STATUS: Error count 1 detected ({errors_count1} errors)")
            if errors_count2 is not None and errors_count2 > 0:
                anomalies.append(f"[{timestamp}] SYS_STATUS: Error count 2 detected ({errors_count2} errors)")
            if errors_count3 is not None and errors_count3 > 0:
                anomalies.append(f"[{timestamp}] SYS_STATUS: Error count 3 detected ({errors_count3} errors)")
            if errors_count4 is not None and errors_count4 > 0:
                anomalies.append(f"[{timestamp}] SYS_STATUS: Error count 4 detected ({errors_count4} errors)")

        # --- Vibration Anomaly Detection (VIBRATION) ---
        if data_type == 'VIBRATION': # This message type may not be present in all logs
            vibration_x = data.get('vibration_x')
            vibration_y = data.get('vibration_y')
            vibration_z = data.get('vibration_z')
            clipping_0 = data.get('clipping_0')
            clipping_1 = data.get('clipping_1')
            clipping_2 = data.get('clipping_2')

            if vibration_x is not None and vibration_x > VIBE_THRESHOLD_RMS_SQ:
                anomalies.append(f"[{timestamp}] VIBRATION: High X-axis vibration detected ({vibration_x:.2f} m/s^2 RMS)")
            if vibration_y is not None and vibration_y > VIBE_THRESHOLD_RMS_SQ:
                anomalies.append(f"[{timestamp}] VIBRATION: High Y-axis vibration detected ({vibration_y:.2f} m/s^2 RMS)")
            if vibration_z is not None and vibration_z > VIBE_THRESHOLD_RMS_SQ:
                anomalies.append(f"[{timestamp}] VIBRATION: High Z-axis vibration detected ({vibration_z:.2f} m/s^2 RMS)")

            if clipping_0 is not None and clipping_0 > 0:
                anomalies.append(f"[{timestamp}] VIBRATION: IMU0 clipping detected ({clipping_0} clips)")
            if clipping_1 is not None and clipping_1 > 0:
                anomalies.append(f"[{timestamp}] VIBRATION: IMU1 clipping detected ({clipping_1} clips)")
            if clipping_2 is not None and clipping_2 > 0:
                anomalies.append(f"[{timestamp}] VIBRATION: IMU2 clipping detected ({clipping_2} clips)")

        # --- GPS Anomaly Detection (GPS_RAW_INT) ---
        if data_type == 'GPS_RAW_INT': # This message type may not be present in all logs
            fix_type = data.get('fix_type')
            eph = data.get('eph') # HDOP in cm
            satellites_visible = data.get('satellites_visible')

            if fix_type is not None and fix_type < 3: # 0-No fix, 1-2D fix, 2-3D fix. 3 is good 3D fix.
                anomalies.append(f"[{timestamp}] GPS_RAW_INT: Poor GPS fix type detected ({fix_type})")
            if eph is not None and eph > GPS_EPH_HIGH_THRESHOLD_CM:
                anomalies.append(f"[{timestamp}] GPS_RAW_INT: High HDOP detected ({eph/100.0:.2f} m)")
            if satellites_visible is not None and satellites_visible < GPS_SATS_LOW_THRESHOLD:
                anomalies.append(f"[{timestamp}] GPS_RAW_INT: Low number of visible satellites ({satellites_visible} sats)")

except FileNotFoundError:
    anomalies.append("Error: 'parsed_telemetry.json' not found.")
except Exception as e:
    anomalies.append(f"Error processing telemetry data: {e}")

if not anomalies:
    result = "No significant anomalies detected."
else:
    # Summarize anomalies by type and count
    anomaly_counts = {}
    for anomaly_msg in anomalies:
        # Extract a concise key for counting
        if "X-acceleration spike" in anomaly_msg: key = "X-accel spike"
        elif "Y-acceleration spike" in anomaly_msg: key = "Y-accel spike"
        elif "Z-acceleration spike" in anomaly_msg: key = "Z-accel spike"
        elif "X-gyro spike" in anomaly_msg: key = "X-gyro spike"
        elif "Y-gyro spike" in anomaly_msg: key = "Y-gyro spike"
        elif "Z-gyro spike" in anomaly_msg: key = "Z-gyro spike"
        elif "Sudden large pressure change" in anomaly_msg: key = "Sudden pressure change (hPa/s)"
        elif "Low battery voltage" in anomaly_msg: key = "Low battery voltage (V)"
        elif "Low battery remaining" in anomaly_msg: key = "Low battery remaining (%)"
        elif "High CPU load" in anomaly_msg: key = "High CPU load (%)"
        elif "Communication errors" in anomaly_msg: key = "Communication errors"
        elif "Error count 1" in anomaly_msg: key = "Error count 1"
        elif "Error count 2" in anomaly_msg: key = "Error count 2"
        elif "Error count 3" in anomaly_msg: key = "Error count 3"
        elif "Error count 4" in anomaly_msg: key = "Error count 4"
        elif "High X-axis vibration" in anomaly_msg: key = "High X-vibration (m/s^2 RMS)"
        elif "High Y-axis vibration" in anomaly_msg: key = "High Y-vibration (m/s^2 RMS)"
        elif "High Z-axis vibration" in anomaly_msg: key = "High Z-vibration (m/s^2 RMS)"
        elif "IMU0 clipping" in anomaly_msg: key = "IMU0 clipping"
        elif "IMU1 clipping" in anomaly_msg: key = "IMU1 clipping"
        elif "IMU2 clipping" in anomaly_msg: key = "IMU2 clipping"
        elif "Poor GPS fix type" in anomaly_msg: key = "Poor GPS fix type"
        elif "High HDOP" in anomaly_msg: key = "High GPS HDOP (m)"
        elif "Low number of visible satellites" in anomaly_msg: key = "Low GPS satellites"
        else: key = "Other anomaly"
        
        anomaly_counts[key] = anomaly_counts.get(key, 0) + 1

    summary_list = ["Detected anomalies:"]
    for key, count in anomaly_counts.items():
        summary_list.append(f"- {key}: {count} occurrence(s)")
    result = "\n".join(summary_list)

