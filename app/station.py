from config import logger
import re

Daliao = ["大寮"]
Siaogang = ["小港"]
Renwu = ["仁武", "鳥松", "三民"]
Zuoying = ["左營"]
Linyuan = ["林園"]
Cianjin = ["前金", "鼓山", "新興", "苓雅", "鹽埕"]
Cianjhen = ["前鎮", "旗津"]
Meinong = ["美濃", "大樹","阿蓮", "燕巢", "大社","那瑪夏", "茂林", "桃源", "甲仙", "六龜", "杉林", "旗山", "內門", "田寮"]
Nanzih = ["楠梓"]
Fongshan = ["鳳山"]
Ciaotou = ["橋頭", "湖內", "岡山", "梓官", "路竹", "永安", "彌陀", "茄萣"]
stations = [Daliao, Siaogang, Renwu, Zuoying, Linyuan,
            Cianjin, Ciaotou, Fongshan, Nanzih, Meinong, Cianjhen]
dist = Daliao+Siaogang+Renwu+Zuoying+Linyuan+Cianjin+Cianjhen+Meinong+Nanzih+Fongshan+Ciaotou

# Example:
# station_id_mapping("高雄市鼓山區蓮海路")->前金
# station_id_mapping("小港區小港路90號")->小港
# station_id_mapping("高雄市彌陀鄉")->橋頭

def station_id_mapping(addr):    
    logger.debug(f"station_id_mapping - addr: {addr}")
    for d in dist:
        pat = d+"[鄉鎮市區]?"
        sta = re.search(pat, addr)
        logger.debug(f"station_id_mapping - pat: {pat}")
        if sta:
            logger.debug(f"station_id_mapping - sta: {sta}")
            sta = sta.group(0)
            sta = re.sub("[鄉鎮市區]$","",sta)
            for station in stations:
                if sta in station:
                    return station[0]
            break
    return None