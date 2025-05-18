import requests
import pandas as pd
from datetime import datetime

def get_f1_drivers_with_team():
    try:
        api_url = 'http://ergast.com/api/f1/current/drivers.json'
        response = requests.get(api_url)
        response.raise_for_status()
        
        data = response.json()
        current_year = datetime.now().year
        
        drivers = []
        for driver in data['MRData']['DriverTable']['Drivers']:
            birth_date = driver['dateOfBirth']
            birth_year = int(birth_date.split('-')[0])
            
            # 取得車隊資訊
            team_url = f"http://ergast.com/api/f1/current/drivers/{driver['driverId']}/constructors.json"
            team_response = requests.get(team_url)
            team_data = team_response.json()
            team_name = 'N/A'
            if team_data['MRData']['total'] != '0':
                team_name = team_data['MRData']['ConstructorTable']['Constructors'][0]['name']
            
            drivers.append({
                '車手號碼': driver.get('permanentNumber', 'N/A'),
                '姓名': f"{driver['givenName']} {driver['familyName']}",
                '國籍': driver['nationality'],
                '出生日期': birth_date,
                '年齡': current_year - birth_year,
                '車手編號': driver['driverId'],
                '車隊': team_name
            })
        
        return pd.DataFrame(drivers)
    except Exception as e:
        print(f"獲取資料失敗: {str(e)}")
        return pd.DataFrame()

# 執行函式並取得結果
result_df = get_f1_drivers_with_team()
print(result_df.head(20))
