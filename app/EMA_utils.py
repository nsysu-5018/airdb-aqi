import math
import pandas as pd

def calculateAlpha(w=0.999, days=1):
    # days = ln(1 - w) / ln(1 - a)
    try:
        alpha = 1 - math.exp(math.log(1 - w) / days)
        return round(alpha, 3)
    except:
        return None

def calculateEMA(df_values, alpha):
    try:
        df_EMA = df_values.ewm(alpha=alpha, adjust=False).mean().round(2)
        result = df_EMA.iloc[-1]
        return result
    except:
        return None