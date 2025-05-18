import fastf1
import pandas as pd

# 啟用快取（需先建立 cache_dir 目錄）
fastf1.Cache.enable_cache('f1_cache')

def get_f1_live_timing():
    try:
        # 獲取當前賽事 session（範例：2025年摩納哥正賽）
        session = fastf1.get_session(2025, 'Jeddah', 'R')

        # 重點！必須先載入數據
        session.load(laps=True, telemetry=True, messages=True)  # 明確指定需加載的數據類型
        
        # 取得位置數據（此時數據已載入）
        pos_data = session.pos_data
        
        # 取得所有圈速資料
        laps = session.laps
        
        # 整理數據（完整範例）
        merged_data = []
        for driver in session.drivers:
            driver_info = session.get_driver(driver)
            team = driver_info.TeamName
            latest_lap = laps.pick_driver(driver).iloc[-1]  # 取最新一圈
            
            merged_data.append({
                'Position': pos_data[driver]['Position'],
                'Driver': driver_info.FullName,
                'Team': team,
                'Gap': pos_data[driver]['GapToLeader'],
                'Tyre': latest_lap['Compound'],
                'LapTime': latest_lap['LapTime']
            })
            
        return pd.DataFrame(merged_data).sort_values('Position')
    
    except Exception as e:
        print(f"數據獲取失敗: {str(e)}")
        return pd.DataFrame()

# 使用範例
df = get_f1_live_timing()
if not df.empty:
    print(df.head())
else:
    print("無可用數據")