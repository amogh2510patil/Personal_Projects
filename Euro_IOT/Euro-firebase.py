import requests
import json
import pandas as pd
import numpy as np
from datetime import date,timedelta
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

#The url to which API calls are to be made
yes = date.today()-timedelta(1)
tom = date.today()+timedelta(1)
url = "https://match.uefa.com/v2/matches?fromDate="+str(yes)+"&toDate="+str(tom)+"&order=ASC&offset=0&limit=100&competitionId=18,39,14,27,38,22,19,2014,2017,5,28,9,1,13,3,2018,101,17,2008,23"

payload={}
headers = {
  'authority': 'match.uefa.com',
  'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
  'sec-ch-ua-mobile': '?0',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
  'x-api-key': 'ceeee1a5bb209502c6c438abd8f30aef179ce669bb9288f2d1cf2fa276de03f4',
  'accept': '*/*',
  'origin': 'https://www.uefa.com',
  'sec-fetch-site': 'same-site',
  'sec-fetch-mode': 'cors',
  'sec-fetch-dest': 'empty',
  'referer': 'https://www.uefa.com/',
  'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
  'if-none-match': '"04e969a048ff4ef412e07f3871a053a10"'
}
#To make a connection with the Google firebase database
cred = credentials.Certificate("Firebase-sdk.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':'https://iot-test-62bb9-default-rtdb.firebaseio.com/'
})
ref=db.reference('/')



try:
    #Function gets the match data from the site with a Get Request
    def GET_DATA(): 
        response = requests.request("GET", url, headers=headers, data=payload)
        dat = response.json()
        df = pd.json_normalize(dat)
        #df.to_csv("Euro2.csv")
        cond = df['competition.metaData.name'] == "European Championship"
        rows = df.loc[cond,['status','kickOffTime.dateTime','awayTeam.internationalName','homeTeam.internationalName','score.total.away','score.total.home']]
        val = np.asarray(rows.values)
        ind1 = np.where(val == 'LIVE')[0]
        match = val[ind1][0]
        return(match)

    data = GET_DATA()
    old_score1 = 0.0
    old_score2 = 0.0
    new_score1 = 0.0
    new_score2 = 0.0

    #Loop runs to check if a Goal Has occured 
    while data[0] == "LIVE" :
        data = GET_DATA()
        new_score1 = float(data[4])
        new_score2 = float(data[5])
        if (new_score1 != old_score1) or (new_score2 != old_score2) :
            print("GOAL")
            #Activating the buzzer for 10 seconds
            ref.set(
                    {
                        'Buzzer_Status':1
                    }
                )
            time.sleep(10)
            #Dectivating the buzzer
            ref.set(
                    {
                        'Buzzer_Status':0
                    }
                )
        old_score1 = new_score1
        old_score2 = new_score2  
        time.sleep(10)

#Error Handling
except:
    print("No Live matches ")
    

    


