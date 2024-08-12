from apscheduler.schedulers.background import BackgroundScheduler
from config import settings
from contextlib import asynccontextmanager
import database
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Query
import pandas as pd
import station
import subprocess
import EMA_utils as EMA


@asynccontextmanager
async def lifespan(app: FastAPI):
    check_update()
    yield


app = FastAPI(lifespan=lifespan)
scheduler = BackgroundScheduler()


@scheduler.scheduled_job('cron', hour = 1, minute = 0)
def check_update():
    subprocess.run(['pytest',  '/code/app/updater.py'])


responses = {
    403: {"description": "Not enough privilege.(ex: IP)"},
    404: {
        "description": "Server can't propcess parameter or find specific resources.",
        "content": {
            "application/json": {
                "example": {"detail": "Error message."},
            },
        },
    },
}


@app.get(
    "/aqi/get",
    responses={
        **responses,
        200: {
            "description": "Find aqi data.",
            "content": {
               "application/json": {
                    "example": {"so2": 1.9, "co": 0.44, "o3": 23.15, "pm10": 49.04, "pm2.5": 29.45, "no2": 16.44, "nox": 17.66, "no": 1.16},
               },
            },
        },
    },
)
def get_aqi_by_addr_date(addr: str = Query(description="高雄市鼓山區蓮海路"), \
                        date: str = Query(description="2023-04-07", regex="^\d{4}\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])$"), \
                        period: int = Query(desciption="30", default=30, gt=0)):
    # show all input parameters
    print("(Input)addr:", addr)
    print("(Input)date:", date)
    print("(Input)period:", period)

    # get sitename by addr input
    sitename = station.station_id_mapping(addr)
    if settings.debug:
        print("sitename:", sitename)
    if sitename is None:
            raise HTTPException(status_code=404, detail="Can't find station.")

    # check there is value at date
    aqi_values = database.get_aqi_by_addr_date(sitename, date, date)
    if aqi_values is None or len(aqi_values) == 0:
        raise HTTPException(status_code=404, detail="Can't find data about " + date + " in database.")

    # calculate start_date
    end_date = date
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
    start_date_obj = end_date_obj - timedelta(days=period-1)
    start_date = start_date_obj.strftime('%Y-%m-%d')
    if settings.debug:
        print("start_date:", start_date)
        print("end_date:", end_date)
    
    # get aqi values from database
    aqi_values = database.get_aqi_by_addr_date(sitename, start_date, end_date)
    if settings.debug:
        print("aqi_values:", aqi_values)
    if aqi_values is None or len(aqi_values) == 0:
        raise HTTPException(status_code=404, detail="Can't find data between " + start_date + " and " + end_date + " in database.")

    # calculate EMA value
    df_values = pd.DataFrame(aqi_values)
    days = min(len(aqi_values), period)  # because there is missvalue in database
    alpha = EMA.calculateAlpha(w=0.999, days=days)
    if alpha is None:
            raise HTTPException(status_code=404, detail="Failed to calcuale alpha.")
    result = EMA.calculateEMA(df_values, alpha)
    if result is None:
            raise HTTPException(status_code=404, detail="Failed to calcuale EMA.")
    if settings.debug:
        print("days:", days)
        print("alpha:", alpha)
        print("EMA result:\n" + str(result))
    
    return {"so2": result[0],
            "co": result[1],
            "o3": result[2],
            "pm10": result[3],
            "pm2.5": result[4],
            "no2": result[5],
            "nox": result[6],
            "no": result[7]}
