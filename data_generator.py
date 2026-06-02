import duckdb
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_toll_database():
    np.random.seed(42)
    con = duckdb.connect()

    vehicles_data = pd.DataFrame({
        "vehicle_id":       range(1, 21),
        "vehicle_class":    (["PKW"]*8 + ["LKW_7.5t"]*5 + ["LKW_18t"]*4 + ["Bus"]*3),
        "registration":     (["DE"]*10 + ["PL"]*4 + ["NL"]*3 + ["FR"]*2 + ["CZ"]*1),
        "toll_rate_per_km": ([0.0]*8 + [0.187]*5 + [0.274]*4 + [0.155]*3)
    })
    con.execute("CREATE TABLE vehicles AS SELECT * FROM vehicles_data")

    segments_data = pd.DataFrame({
        "segment_id":   range(1, 6),
        "segment_name": ["A1_Nord","A9_Sued","A100_Berlin","A2_Ost","A7_West"],
        "length_km":    [45.2, 62.8, 11.5, 78.4, 53.1],
        "toll_zone":    ["Nord","Sued","Berlin","Ost","West"]
    })
    con.execute("CREATE TABLE segments AS SELECT * FROM segments_data")

    dates = pd.date_range("2024-01-01", "2024-06-30")
    calendar_data = pd.DataFrame({
        "date_id":     range(1, len(dates)+1),
        "date":        dates,
        "week_number": dates.isocalendar().week.values,
        "month":       dates.month,
        "month_name":  dates.strftime("%B"),
        "day_name":    dates.strftime("%A"),
        "is_weekend":  (dates.dayofweek >= 5).astype(int)
    })
    con.execute("CREATE TABLE calendar AS SELECT * FROM calendar_data")

    records = []
    tid = 1
    for day_offset in range(182):
        date = datetime(2024, 1, 1) + timedelta(days=day_offset)
        is_weekend = date.weekday() >= 5
        for seg_id in range(1, 6):
            seg = segments_data.iloc[seg_id - 1]
            for hour in range(24):
                if 7 <= hour <= 9 or 17 <= hour <= 19:
                    n = np.random.randint(40, 80)
                elif 22 <= hour or hour <= 5:
                    n = np.random.randint(5, 20)
                else:
                    n = np.random.randint(20, 45)
                if is_weekend:
                    n = int(n * 0.6)
                for _ in range(n):
                    vid = np.random.randint(1, 21)
                    veh = vehicles_data.iloc[vid - 1]
                    toll = round(veh["toll_rate_per_km"] * seg["length_km"] * np.random.normal(1.0, 0.05), 4)
                    records.append({
                        "transaction_id": tid,
                        "vehicle_id": vid,
                        "segment_id": seg_id,
                        "date_id": day_offset + 1,
                        "hour": hour,
                        "toll_amount": max(toll, 0)
                    })
                    tid += 1

    transactions_df = pd.DataFrame(records)
    con.execute("CREATE TABLE toll_transactions AS SELECT * FROM transactions_df")
    return con
