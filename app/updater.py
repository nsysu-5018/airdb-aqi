import codecs
import csv
import database
from datetime import datetime, timedelta
import pandas as pd
from playwright.sync_api import Page
import pytz


def do_action(page, start_time, end_time, filename):
    # Navigate to url
    page.goto("https://airtw.moenv.gov.tw/CHT/Query/InsValue.aspx")

    # 1. 填入測站
    # Click on '地區'
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
    page.locator('input[value="確認"]').click()

    # 2. 填入測項
    # Click on '測項'
    page.locator(".select2-selection").click()
    # Click on 'CO'
    page.locator('[id^=select2-ddl_Item-result-][id$="-CO"]').click()
    # Click on '測項'
    page.locator(".select2-selection").click()
    # Click on 'O3'
    page.locator('[id^=select2-ddl_Item-result-][id$="-O3"]').click()
    # Click on '測項'
    page.locator(".select2-selection").click()
    # Click on 'NO'
    page.locator('[id^=select2-ddl_Item-result-][id$="-NO"]').click()
    # Click on '測項'
    page.locator(".select2-selection").click()
    # Click on 'SO2'
    page.locator('[id^=select2-ddl_Item-result-][id$="-SO2"]').click()
    # Click on '測項'
    page.locator(".select2-selection").click()
    # Click on 'NO2'
    page.locator('[id^=select2-ddl_Item-result-][id$="-NO2"]').click()
    # Click on '測項'
    page.locator(".select2-selection").click()
    # Click on 'NOx'
    page.locator('[id^=select2-ddl_Item-result-][id$="-NOx"]').click()
    # Click on '測項'
    page.locator(".select2-selection").click()
    # Click on 'PM2.5'
    page.locator('[id^=select2-ddl_Item-result-][id$="-PM2.5"]').click()
    # Click on '測項'
    page.locator(".select2-selection").click()
    # Click on 'PM10'
    page.locator('[id^=select2-ddl_Item-result-][id$="-PM10"]').click()

    # 3. 填入開始時間
    # Click on '開始時間'
    page.locator("#CPH_Content_txt_Stime").click()
    # Type on '開始時間'
    page.locator("#CPH_Content_txt_Stime").fill(start_time)

    # 4. 填入結束時間
    # Click on '結束時間'
    page.locator("#CPH_Content_txt_Etime").click()
    # Type on '結束時間'
    page.locator("#CPH_Content_txt_Etime").fill(end_time)

    # 5. 下載
    # Click on '下載'
    with page.expect_download() as download_info:
        page.locator("#CPH_Content_btnDownload").click()
    download = download_info.value
    download.save_as(filename)


def csv2utf8(filename):
    # big5 to utf-8
    input_file = filename
    output_file = input_file.replace(".csv", "_utf8.csv")

    with codecs.open(input_file, "r", encoding="big5") as file:
        csv_data = csv.reader(file)

        # drop unnecessary information
        header = next(csv_data)
        header = next(csv_data)

        with open(output_file, "w", encoding="utf-8", newline="") as output:
            csv_writer = csv.writer(output)

            for row in csv_data:
                csv_writer.writerow(row)

    return output_file


def csv2df(filename):
    # read data from csv
    # post-processing data and save into dataframe
    df = pd.read_csv(filename)
    df.set_index(["測站", "日期", "測項"], inplace=True)
    df = df.apply(pd.to_numeric, errors="coerce")
    df["average"] = df.mean(axis=1).round(2)
    df.reset_index(inplace=True)
    df = df[["測站", "日期", "測項", "average"]]

    keys = [
        "sitename",
        "datacreationdate",
        "so2",
        "co",
        "o3",
        "pm10",
        "pm2.5",
        "no2",
        "nox",
        "no",
    ]
    df_result = pd.DataFrame(columns=keys)

    grouped_df = df.groupby(["測站", "日期"])
    for group_name, group_data in grouped_df:

        so2_avg = group_data[group_data["測項"] == "SO2"]["average"].values[0]
        co_avg = group_data[group_data["測項"] == "CO"]["average"].values[0]
        o3_avg = group_data[group_data["測項"] == "O3"]["average"].values[0]
        pm10_avg = group_data[group_data["測項"] == "PM10"]["average"].values[0]
        pm25_avg = group_data[group_data["測項"] == "PM2.5"]["average"].values[0]
        no2_avg = group_data[group_data["測項"] == "NO2"]["average"].values[0]
        nox_avg = group_data[group_data["測項"] == "NOx"]["average"].values[0]
        no_avg = group_data[group_data["測項"] == "NO"]["average"].values[0]

        new_row = {
            "sitename": group_name[0],
            "datacreationdate": group_name[1],
            "so2": so2_avg,
            "co": co_avg,
            "o3": o3_avg,
            "pm10": pm10_avg,
            "pm2.5": pm25_avg,
            "no2": no2_avg,
            "nox": nox_avg,
            "no": no_avg,
        }
        df_result.loc[len(df_result)] = new_row

    df_result["datacreationdate"] = pd.to_datetime(
        df_result["datacreationdate"]
    ).dt.strftime("%Y-%m-%d")
    df_result.sort_values(by=["datacreationdate"], inplace=True)
    return df_result


def test_start(page: Page):
    output_file = '/tmp/tmp.csv'
    taipei_tz = pytz.timezone('Asia/Taipei')
    print("Running task_daily_update_db...")
    print(datetime.now(tz=taipei_tz))

    # check if database is up to date
    db_max_date = database.get_max_datacreationdate()[0]
    db_max_date = db_max_date.replace("-", "/")
    today_date_obj = datetime.now(tz=taipei_tz).date()

    # start date is the next day of db_max_date
    start_date_obj = datetime.strptime(db_max_date, '%Y/%m/%d').date() + timedelta(days=1)
    start_date = start_date_obj.strftime('%Y/%m/%d')

    # end date is yesterday
    # because there is missing value today
    end_date_obj = today_date_obj - timedelta(days=1)
    end_date = end_date_obj.strftime('%Y/%m/%d')

    if db_max_date != end_date:
        # mean database is not up to date
        print("Update database...")
        print(start_date, "-", end_date)
        do_action(page, start_date, end_date, output_file)
        output_file_utf8 = csv2utf8(output_file)
        df = csv2df(output_file_utf8)
        
        if df is not None:
            database.insert_aqi_from_df(df)
            print("Finish update database.")
    else:
        print("Database is up to date.")
