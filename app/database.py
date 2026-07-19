import sqlite3

conn = sqlite3.connect("/mnt/aqi-app/airdb.db", check_same_thread=False)

if conn is None:
    print("Failed to connect airdb.db!!!")
    exit(1)

cur = conn.cursor()


def get_all_aqi():
    cursor = cur.execute("SELECT * FROM aqi")
    return cursor.fetchall()


def get_aqi_by_addr_date(addr: str, start_date: str, end_date: str):
    sql = (
        'SELECT so2, co, o3, pm10, "pm2.5", no2, nox, no \
            FROM aqi \
            WHERE sitename="%s" \
            AND date(datacreationdate) BETWEEN "%s" AND "%s"'
        % (addr, start_date, end_date)
    )
    cursor = cur.execute(sql)
    return cursor.fetchall()


def insert_aqi_from_df(df):
    cols = ["sitename", "datacreationdate", "so2", "co", "o3", "pm10", "pm2.5", "no2", "nox", "no"]
    quoted_cols = [f'"{c}"' for c in cols]
    cur.executemany(
        f"INSERT OR IGNORE INTO aqi ({', '.join(quoted_cols)}) VALUES({', '.join(['?']*len(cols))})",
        df[cols].values.tolist(),
    )
    conn.commit()


def get_max_datacreationdate():
    sql = "SELECT MAX(datacreationdate) FROM aqi"
    cursor = cur.execute(sql)
    return cursor.fetchone()
