import database
from datetime import date, datetime, timedelta
import pandas as pd
from playwright.sync_api import Page
import pytz


def download_air_quality_csv(page: Page, start_date: date, end_date: date, output_file: str):
    # Navigate to url
    page.goto("https://airtw.moenv.gov.tw/CHT/Query/InsValue.aspx")

    # 1. 填入測站
    # Click on '測站' input field
    page.locator("#a_site").click()
    # Click on '高屏空品區'
    page.locator("#ui-id-9").click()
    # Click on '復興'
    page.locator("#site51").click()
    # Click on '美濃'
    page.locator("#site40").click()
    # Click on '鳳山'
    page.locator("#site68").click()
    # Click on '橋頭'
    page.locator("#site71").click()
    # Click on '楠梓'
    page.locator("#site60").click()
    # Click on '左營'
    page.locator("#site17").click()
    # Click on '仁武'
    page.locator("#site13").click()
    # Click on '大寮'
    page.locator("#site9").click()
    # Click on '小港'
    page.locator("#site10").click()
    # Click on '前金'
    page.locator("#site35").click()
    # Click on '前鎮'
    page.locator("#site36").click()
    # Click on '林園'
    page.locator("#site32").click()
    # Click on '確認'
    page.locator('#btn_ConfirmSites').click()

    # 2. 填入測項
    # Click on SO2, CO, O3, PM10, PM2.5, NO2, NOx, NO
    page.locator('#ddl_Item').select_option(['SO2', 'CO', 'O3', 'PM10', 'PM2.5', 'NO2', 'NOx', 'NO'], force=True);

    # 3. 填入開始時間
    # Type on '開始時間'
    start_date_str = start_date.strftime("%Y/%m/%d")
    page.locator("#CPH_Content_txt_Stime").fill(start_date_str)

    # 4. 填入結束時間
    # Type on '結束時間'
    end_date_str = end_date.strftime("%Y/%m/%d")
    page.locator("#CPH_Content_txt_Etime").fill(end_date_str)

    # 5. Click on '查詢'
    page.locator("#btnQuery").click()

    # 6. 下載
    # Click on '下載'
    with page.expect_download() as download_info:
        page.locator("#CPH_Content_btn_download").click()
    download = download_info.value
    download.save_as(output_file)

def process_data(csv_file: str):
    # Convert csv to dataframe for easy data processing
    df = pd.read_csv(csv_file, skiprows=2)

    # Format date column from yyyy/mm/dd to yyyy-mm-dd
    date_column = '日期'
    df[date_column] = pd.to_datetime(df[date_column], format='%Y/%m/%d').dt.strftime('%Y-%m-%d')

    hour_columns = [ f'{h:02d}' for h in range(24)]
    # coerce only the hour columns — errors='coerce' replaces any non-numeric values with NaN
    df[hour_columns] = df[hour_columns].apply(pd.to_numeric, errors='coerce')

    # Average the row among the day (rounds the values to 2 decimal places.)
    df['average'] = df[hour_columns].mean(axis=1, skipna=True).round(2) # axis=1 averages in a row-wise direction

    # Drop hour columns
    df = df.drop(columns=hour_columns)

    # Groups rows by the combination of 測站 and 日期, spreads the distinct 測項 values (SO2, CO, O3...) into their own columns, and fills each with the corresponding average
    #   By perform the grouping, the columns '測站', '日期' becomes a MultiIndex and not 2 columns
    df = df.pivot(index=['測站', date_column], columns='測項', values='average')

    # Reorder the air quality values to the database column order
    df = df[['SO2', 'CO', 'O3', 'PM10', 'PM2.5', 'NO2', 'NOx', 'NO']]

    # Brings 測站/日期 back as real columns
    df = df.reset_index()

    # Rename columns to match database columns
    df = df.rename(columns={
        "測站": "sitename",
        "日期": "datacreationdate",
        "SO2": "so2",
        "CO": "co",
        "O3": "o3",
        "PM10": "pm10",
        "PM2.5": "pm2.5",
        "NO2": "no2",
        "NOx": "nox",
        "NO": "no",
    })

    # removes the "測項" label from the columns axis metadata
    df.columns.name = None

    # temporary check
    # df.to_csv(f"temp.csv", index=False)

    return df


def test_start(page: Page):
    downloaded_air_quality_csv_file = '/tmp/air-quality.csv'
    taipei_tz = pytz.timezone('Asia/Taipei')
    today = datetime.now(tz=taipei_tz).date()
    print(f"Running daily airdb.db at {today}")
    
    # start date is the next day of db_max_date
    db_max_date_str = database.get_max_datacreationdate()[0]
    db_max_date = date.fromisoformat(db_max_date_str)
    start_date = db_max_date + timedelta(days=1)

    # end date is yesterday
    # because there is missing value today
    end_date = today - timedelta(days=1)

    if db_max_date != end_date:
        print("Update database...")
        print(f"{start_date} - {end_date}")
        download_air_quality_csv(page, start_date, end_date, downloaded_air_quality_csv_file)
        processed_air_quality_dataframe = process_data(downloaded_air_quality_csv_file)
        database.insert_aqi_from_df(processed_air_quality_dataframe)
        print("Finish update database.")
    else:
        print("Database is up to date.")
