@echo off
mongod --quiet
sudo net start MongoDB
mongorestore --db ORLAB ./dbdump --quiet
start "orserver" python backend/server.py
