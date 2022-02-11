# WhoIsHomeUI
A webapp that scans your network and allows you to track hosts, give email updates and possibly more!

First install Docker and Docker Compose on your Raspberry Pi (or other similar device) following the link until step 5:
https://dev.to/elalemanyo/how-to-install-docker-and-docker-compose-on-raspberry-pi-1mo

In the index of this repo type: "docker-compose up -d"

The container should now be up and running on your localhost:8000.

Go to ip:8000/admin and login.
Username: admin
password: admin123

Go to scanner config on the left and change the following values:

Internet interface should be: "eth0" for a wired ethernet connection. If your raspberry pi is using wifi use "wlp2s0" or type "ifconfig" in command line to get the active interface name.

leave ARP-STRING as is.

IP Subnet: change this to the net your router uses. for me it uses 192.168.2.1 - 192.168.2.198 so set here ONLY 192.168.2. (dont forget last dot)
Ip range start (first IP to scan within earlier specified range)
IP range end (last IP to scan within earlier specified range).

If you want email notifications set up email config as well.

Go to ip:8000/settings/

Enable scanner status and you should be up and running!
