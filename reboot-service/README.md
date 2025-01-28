# Restart the services on reboot of the server.

```
cp start-monitoring-tool-on-reboot.service /etc/systemd/system/start-monitoring-tool-on-reboot.service

sudo systemctl daemon-reload
sudo systemctl enable start-monitoring-tool-on-reboot.service
sudo systemctl start start-monitoring-tool-on-reboot.service

```
