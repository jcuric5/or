@echo off
mongoexport --uri "mongodb+srv://josipcuric:1234@or.g7eeo.mongodb.net/" --db ORLAB --collection ZagrebPristupacnostParkova --out ./ZagrebPristupacnostParkova.json.temp --jsonArray --quiet
jq "map(del(._id) + {\"@context\": {\"@vocab\": \"http://schema.org/\", location: \"GeoCoordinates\", area: \"area\"}})" ./ZagrebPristupacnostParkova.json.temp > ./ZagrebPristupacnostParkova.json
del /Q "./ZagrebPristupacnostParkova.json.temp"
