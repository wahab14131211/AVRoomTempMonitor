#! /home/avadmin/Scripts/TempMonitor/venv/bin/python3

#import modules to read data from sensor
import time
import board
import adafruit_dht
#import modules to upload to googlesheets
import gspread
from oauth2client.service_account import ServiceAccountCredentials
#import modules for sending email
import os
import configparser
import smtplib
from email.message import EmailMessage

sensor = adafruit_dht.DHT22(board.D24, use_pulseio=True)
MAX_ALLOWED_TEMP = 35
EMAIL_LIST = "audiovideo.mississauga@ahmadiyya.ca"
temperature = -99
humidity = 0
dateTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

#get values from the sensor
while (temperature == -99):
    try:
        temperature = sensor.temperature
        humidity = sensor.humidity
        print("Current Time is {}, Temp={}C, Humidity={}%".format(dateTime,temperature,humidity))
        sensor.exit()
    except RuntimeError as error:
        print(error.args[0])
        time.sleep(2)
        continue
    except Exception as error:
        sensor.exit()
        raise error

#Setup google drive and sheets API
scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive",
       ]
creds = ServiceAccountCredentials.from_json_keyfile_name("/home/avadmin/Scripts/TempMonitor/avroom-temp-monitor-key.json", scope)
client = gspread.authorize(creds)
sheet = client.open("AVRoom Temp and Humidity Monitoring").get_worksheet(1)

#get max_temp value from spreadsheet, if it exists
spreadSheetMaxTemp = sheet.acell("G2").value
if (spreadSheetMaxTemp and spreadSheetMaxTemp.isdigit()):
    MAX_ALLOWED_TEMP = float(spreadSheetMaxTemp)
spreadSheetEmailList = sheet.acell("G3").value
if (spreadSheetEmailList):
    EMAIL_LIST = spreadSheetEmailList
#append data to spreadsheet
data = [dateTime,temperature,humidity,MAX_ALLOWED_TEMP]
sheet.append_row(data)

#Send email if temp is out of acceptable range
print ("Max temperature for email notification is: {}".format(MAX_ALLOWED_TEMP))
print ("Email List is: {}".format(EMAIL_LIST))
if (temperature >= MAX_ALLOWED_TEMP):
    if (not os.path.exists('.current_overtemp_email_sent')):
        #read email login details from config.ini file:
        config = configparser.ConfigParser()
        config.read('config.ini')

        msg = EmailMessage()
        msg.set_content("""
Assalam-o-Alaikum,
The automated temperature monitoring system installed in the Mississauga Mosque AVRoom Rack has exceeded the max allowed value of {} degrees celcius.
Prolonged exposure to this temperature can cause pre-mature failure of key devices, such as the audio mixers.

Please do something to decrease the temperature in the Mississauga Mosque AVRoom ASAP.

Jazakallah

Note1: you can view the historical temperature data in this room by accessing the following spreadsheet: https://docs.google.com/spreadsheets/d/1-Kfv4jkbDoB5De1hfu10NmyE1wgMmUuG0wfw4OeWqME/edit?usp=sharing

Note2: max temp of the BLU signal processors (used as audio mixers) is 35 degrees: https://adn.harmanpro.com/static/archimedia/aa_help/Device_Help_Files/BSS_Soundweb_London/BLU_Devices_Technical_Specifications.htm
""".format(MAX_ALLOWED_TEMP))
        msg['Subject'] = "WARNING: Temperature in Mississauga Mosque AVRoom Rack Exceeded {} degrees".format(MAX_ALLOWED_TEMP)
        msg['From'] = config["senderEmail"]["email"]
        msg['To'] = EMAIL_LIST

        server = smtplib.SMTP('smtp.gmail.com',587)
        server.starttls()
        server.login(config["senderEmail"]["email"], config["senderEmail"]["password"])
        server.send_message(msg) 
        server.quit()
        print("Warning Email Sent")

        with open('.current_overtemp_email_sent', 'w') as fp:
            pass
    else:
        print("Skip sending email, since it was previously sent")

#add hysteresis to prevent email spam
if (temperature <= MAX_ALLOWED_TEMP - 2):
    if (os.path.exists('.current_overtemp_email_sent')):
        os.remove('.current_overtemp_email_sent')
