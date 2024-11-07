@echo off
taskkill /FI "WindowTitle eq orserver*" /T /F
sudo net stop MongoDB
