# WhoIsHomeUI

WhoIsHomeUI is a webapp that scans your network and allows you to track hosts, give email updates, see new MAC addresses who connect to your network and possibly more in the future!

The webapp runs on Django and the network scanning is done by the linux tool arp-scan. (for the cli email alert version check: https://github.com/DartLazer/WhoIsHome)
This project started as a way for me to learn Python and Django a while back. After a few friends liked my tool I decided to put it on here for everyone to use. If you have any comments, tips on my coding, or feature requests. Please open an issue and I will see to it.

At the tool's current state the Django server is ran in Debug mode with the development webserver. I do therefore \***\*NOT\*\*** recommend running this on an open port to the Internet. In a future update I will probably ship this with a proper webserver, depending on how much people will actually use the service.

WhoIsHomeUI scans devices on your network using ARP-Scan. It keeps track of all hosts, based on MAC Addresses in a database.
The system registers a device "away from home" when it misses a certain amount of scans. The "not home threshold". I would recommend leaving this at around 20, since Apple devices tend to disconnect from the network a lot to save battery power. Lowering this value will cause a lot of false departures from Apple devices.

\***\*Update Instructions\*\***
Unless otherwise stated in the changelog section ### Update Instructions

- In the folder containing whoishomeui: `git pull`
- Then the following command `docker-compose up -d --build` (if this does not work try adding sudo in front)
- That should be it!

n.b - if you're upgrading from v0.17 to v0.18, all the historical data will be lost. you can follow the below commands to export data from previous db to new db path

> docker-compose down <br/>
> docker-compose -it app bash <br/>
> \# copy /mysite/db.sqllite3 /dbstore/db_whoih.sqlite3 <br/>
> \# exit <br/>
> docker-compose up -d

\***\*Installation Instructions\*\***

- First install Docker and Docker Compose on your Raspberry Pi (or other similar device, hereafter referenced to as raspberry pi) following the link upto and including step 6:
  https://dev.to/elalemanyo/how-to-install-docker-and-docker-compose-on-raspberry-pi-1mo
- Git clone this repo to your raspberry pi: `git clone https://github.com/babanomania/WhoIsHomeUI`
- Copy the .env.sample file to .env and change the TimeZone and port number if needed
- In the cloned folder execute the following command: `docker-compose up -d`
- The container should now be up and running on your your_raspberrypi_ip_address:8000
- In your webbrowser go to `your_rasppberrypi_ip_address:8000/`
- Go to the settings page and go to the Scanner Settings section:
- Not Home Threshold (The amount of scans a device has to miss, to be considered to have left home). I would recommend leaving this to around 20. iPhones tend to disconnect sometimes. Leaving this on a lower value will register a lot of disconnects from Apple devices.
- Internet interface should be: "eth0" for a wired ethernet connection. If your raspberry pi is using wifi use "wlp2s0" or type "ifconfig" in command line to get the active interface name.
- IP Subnet: change this to the net your router uses. for me it uses `192.168.2.1 - 192.168.2.198` so set here ONLY 192.168.2. (dont forget last dot)
- IP range start (first IP to scan within earlier specified range)
- IP range end (last IP to scan within earlier specified range).
- Press SAVE. Let the page reload and now enable the scanner
- If you want email notifications set up email settings as well.
- In the email body and subject you can access the following variables by putting them in curly brackets {}
- target (gives target name), arrival_time, departure_time , time_away, time_home.

- Go to `your_raspberrypi_ip_addres:8000/settings/`

- Enable scanner status and you should be up and running!

\***\*Enabling on system boot\*\***

To enable WhoIsHomeUI to run on system boot we'll add a command to crontab to execute the docker-compose up -d command at system boot.

- Note the installation of your WhoIsHomeUI installation (use `pwd` command in the installation directory)
- On your raspberry pi enter the following command `sudo crontab -e`
- (If it asks you which editor to use just use your preffered one)
- Hold the down arrow key until you reach the end of the comments block and enter the following code
- `@reboot docker-compose -f directory_from_first_step/docker-compose.yml up -d`
- That's it!
