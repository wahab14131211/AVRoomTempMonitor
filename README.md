This Script uses a raspberry pi zero w and a DHT22 temperature/humidity sensor to monitor and store the temp/humidity values in a google sheet. It also allows the user to specify a temp threshold and will email the user if the measured value exceeds the threshold.

To use this script, you must:
1. create a google sheet with the name "AVRoom Temp and Humidity Monitoring" (or update the string in the script with a custom name).
2. Populate the following cells in the google sheet:
3. A1 = "DateTime", A2 = "Temperature [C]", A3 = "Humidity [%]", A4 = "Temp Threshold", F1 = "Script Monitoring Variables", F2 = "Temperature Threshold (for email notification):", F3 = "Email notification list (comma seperated list):"
4. Then, populate cells G2 and G3 with the temperature threshold (in C) and cell G3 with a comma seperated list of emails to be notified when the threshold is reached.
5. Follow steps 1-13 of the following link: https://spreadsheetpoint.com/python-google-sheets/, save the json API on the pi, and modify the script to read the json api file.
6. give the service account permission to edit the spreadsheet created in step 1 above.
7. follow the steps in https://mailmeteor.com/blog/gmail-smtp-settings to setup an app password for the email which will sent the notification, and store the username and password in the creds.ini file.
8. setup a crontab to tun the AVRommTempMonitor Script periodically.
