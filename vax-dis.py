import requests
import pandas as pd

date = "19-07-2021"
url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict?district_id=294&date="+date

#Getting Data
response = requests.request("GET", url)
dat = response.json()
df = pd.json_normalize(dat['sessions'])
pd.set_option("display.max_rows", 1000)
#df.to_csv("vax_data_BBMP.csv",index=False) #Uncomment to save the details to a csv File
#Selection of centres
centres = [563813,696150,696150,406895,683148,406889,577774]
cond = df['center_id'].isin(centres)

#Telegram Channel
telegram_chat_id = "@temperature_alert_test"         
#Telegram Bot
telegram_bot_id = "bot1601229322:AAH0JzPz-hpdSxCtFfCMGNTQypwg2H_lO8s"
#Necessary Details
rows = df.loc[cond,["center_id","name","available_capacity","vaccine"]]
url = "https://api.telegram.org/" + telegram_bot_id + "/sendMessage"


vals = rows.values.tolist()
msg1 = "Vaccination Details : "
data = {
                "chat_id": telegram_chat_id,
                "text": msg1
                }
response = requests.request("POST",url,params=data)

#Posting the data to the channel
for row in vals:
    msg = str(row[1]) + " \n No: of doses :" + str(row[2]) + " " + str(row[3])
    data = {
                "chat_id": telegram_chat_id,
                "text": msg
                }
    response = requests.request("POST",url,params=data)


