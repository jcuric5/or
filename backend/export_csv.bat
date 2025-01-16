@echo off
mongoexport --uri "mongodb+srv://josipcuric:1234@or.g7eeo.mongodb.net/" --db ORLAB --collection ZagrebPristupacnostParkova --out ./ZagrebPristupacnostParkova.csv --type=csv --fields name,location,area,purpose,entrances,nearest_bus_stop,nearest_tram_stop,nearest_train_stop,nearest_parking --quiet
