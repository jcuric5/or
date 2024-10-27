@echo off
mongod --quiet
sudo net start MongoDB
mongorestore --db ORLAB ./dbdump --quiet
mongoexport --db ORLAB --collection ZagrebPristupacnostParkova --out ./ZagrebPristupacnostParkova.csv --type=csv --fields name,location,area,purpose,entrances,nearest_bus_stop,nearest_tram_stop,nearest_train_stop,nearest_parking --quiet
sudo net stop MongoDB
