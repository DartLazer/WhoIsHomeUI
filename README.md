# WhoIsHomeUI

WhoIsHomeUI is a webapp that scans your network and allows you to track hosts, give email updates, see new MAC addresses who connect to your network and possibly more in the future!

The webapp runs on Django and the network scanning is done by the linux tool arp-scan. (for the cli email alert version check: https://github.com/DartLazer/WhoIsHome)
This project started as a way for me to learn Python and Django a while back. After a few friends liked my tool I decided to put it on here for everyone to use. If you have any comments, tips on my coding, or feature requests. Please open an issue and I will see to it.

At the tool's current state the Django server is ran in Debug mode with the development webserver. I do therefore ****NOT**** recommend running this on an open port to the Internet. In a future update I will probably ship this with a proper webserver, depending on how much people will actually use the service.

WhoIsHomeUI scans devices on your network using ARP-Scan. It keeps track of all hosts, based on MAC Addresses in a database. 
The system registers a device "away from home" when it misses a certain amount of scans. The "not home threshold". I would recommend leaving this at around 20, since Apple devices tend to disconnect from the network a lot to save battery power. Lowering this value will cause a lot of false departures from Apple devices.

****Installation Instructions****
  - First install Docker and Docker Compose on your Raspberry Pi (or other similar device) following the link upto and including step 6:
https://dev.to/elalemanyo/how-to-install-docker-and-docker-compose-on-raspberry-pi-1mo
  - Git clone thise repo to your raspberry pi: "git clone https://github.com/DartLazer/WhoIsHomeUI"
  - In the cloned folder execute the following command: "docker-compose up -d"
  - The container should now be up and running on your your_raspberrypi_ip_addres:8000
  - In your webbrowser go to your_rasppberrypi_ip_address:8000/admin
  - Username: admin
  - Password: admin123

  - Go to scanner config on the left and change the following values:
  - Not Home Threshold (The amount of scans a device has to miss, to be considered to have left home). I would recommend leaving this to around 20. iPhones tend to disconnect sometimes. Leaving this on a lower value will register a lot of disconnects from Apple devices.

  - Internet interface should be: "eth0" for a wired ethernet connection. If your raspberry pi is using wifi use "wlp2s0" or type "ifconfig" in command line to get the active interface name.

  - Leave ARP-STRING as is.

  - IP Subnet: change this to the net your router uses. for me it uses 192.168.2.1 - 192.168.2.198 so set here ONLY 192.168.2. (dont forget last dot)
  - Ip range start (first IP to scan within earlier specified range)
  - IP range end (last IP to scan within earlier specified range).

  - If you want email notifications set up email config as well.

  - Go to ip:8000/settings/

  - Enable scanner status and you should be up and running!
