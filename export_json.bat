@echo off
mongod --quiet
sudo net start MongoDB
mongorestore --db ORLAB ./dbdump --quiet
mongoexport --db ORLAB --collection ZagrebPristupacnostParkova --out ./ZagrebPristupacnostParkova.json.temp --jsonArray --quiet
jq "map(del(._id))" ZagrebPristupacnostParkova.json.temp > ZagrebPristupacnostParkova.json
del /Q "./ZagrebPristupacnostParkova.json.temp"
sudo net stop MongoDB
