# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)

## [0.70] - 2024-11-8

### DockerHub image available
- **DockerHub image available** The project is now using a DockerHub image for easier deployment. It's already in use in
  the docker-compose file, so no changes are needed to use it. This should speed up the deployment process and make it easier.

### Bugfixes

- **Horizontal device history chart** Fixed a bug where the horizontal device history chart was not displaying correctly
- **Styling issues** on several pages fixed

### Changes

- **Continued major code refactor** so the project will be more maintanable and hopefully easier to contribute to in the
  future
- **Updated the readme with new screenshots** to reflect the new changes

### Update Instructions

- Since the repo uses Docker-Hub images now running `docker compose up` should be sufficient after running `git pull`.
- If you encounter an issue where the Docker image is not compatible with your platform or architecture, follow these steps to build the image locally:
  ```bash
  cd ~/WhoIsHomeUI  # Adjust to your local path
  docker build -t dartlazer/whoishome-ui:v0.7 .
  docker compose up
  ```

## [0.6] - 2024-11-7

### New Additions

- **Added custom Device Types** As requested by Mjolinir in pull request 28
- **Updated to latest Bootstrap icons**

### Bug fixes

- **Minor bugfixes and code refactor**

### Update Instructions

- Run `docker-compose build --no-cache` followed by `docker-compose up -d` to rebuild and apply all changes without
  caching.

## [0.54] - 2024-11-02

### Minor updates

- Make device type list alphabetical and title case
- Code cleanup
- Change color palette slightly
- Other minor visual changes

### Update Instructions

- Run `docker-compose build --no-cache` followed by `docker-compose up -d` to rebuild and apply all changes without
  caching.

## [0.52] - 2024-10-30

### Major Fixes

- **Fixed critical, breaking issues in Docker configuration**: The application is now fully usable after resolving
  Docker-related problems that previously impacted functionality.
- **Switched Docker base image**: Replaced the `python:3-buster` base image with `python:3.10-slim-buster` for improved
  to allow latest version of arp-scan to be used. Which will majorly improve **device manufacturer detection**.

### Added

- **Codebase Refactoring**: Improved readability and maintainability by refactoring early project code, aligning with
  best practices.
- **Updated Styling**: Redesigned elements for a modern look and enhanced user experience.
- **ARM Compatibility**: Fixed `curl` library support for ARM architectures, restoring functionality on Raspberry Pi
  devices.

### Minor fixes

- Text overflow issues on the home page
- Updated screenshots in the README
- Remote version not showing on update page

### Update Instructions

- Run `docker-compose build --no-cache` followed by `docker-compose up -d` to rebuild and apply all changes without
  caching.

## [0.40] - 2023-08-29

### Added

- **Telegram Notifications**.
  Telegram notifications are now available on the settings page. Only requirements are Token ID and chat ID.
  [How to get your telegram bot token and chat ID](https://advancedweb.hu/the-easiest-way-to-set-up-a-chat-with-your-telegram-bot/)

- **Auto Delete Logs Setting**
  On the settings page under app settings you can now set auto_delete_logs setting. Setting it to 0 means keeping
  forever
- **Updated readme** to reflect telegram notifcations.

### Updated

- Updated requirements.txt to use Django 4.2, and update requests and django-crispy-forms

### Update Instructions

- Run `git pull` and after updating `docker compose up --build -d`
-

## [0.37] - 2023-02-16

Added **Curfew Mode**.
Curfew mode overrules the normal notification modes and **only** sends notifications for curfew enabled devices, durfing
curfew times.
You could enable curfew mode for i.e. devices for your kids, which shouldn't be online during curfew times.

### Update Instructions

- Run `git pull` and after updating `docker compose up --build -d`

## [0.36] - 2022-12-18

Change to DockerFile to prevent being stuck on `Watching for file changes with StatReloader`

## [0.35] - 2022-09-21

Password support added. App can now be locked by password on the settings page.

## [0.34] - 2022-08-27

Timeline can now also be set to 24 hours and 3 days.
Changed colors of settings page buttons

## [0.33] - 2022-08-21

Added the option to show all devices ever connected to the network.

### Added

- Added new model: HomePageSettingsConfig and related forms for future homepage options
- Added button that displays all devices on homepage

- ### Added
- Some code clean-up here and there

### IMPORTANT Update Instructions when upgrading from a version < 0.3

Version 0.3 marks the migration of the database into a separate docker volume in preparation of launching to Docker-Hub
This update requires some extra instructions

- Migration of the database file will lead to having to manually restore the database.
- Open a terminal in the root folder of your WhoIsHomeUI installation.
- Backup the current db just to be sure `cp mysite/db.sqlite3 db_backup.sqlite3`
- Run: `docker-compose down && git pull && docker-compose up -d --build`
- When the build is finished shut down the container using `docker-compose down`
- Run: (this will create the docker volume required, put your old database in it, and remove the dummy container)

```bash
docker container create --name dummy -v whoishomeui_dbstore:/mnt/test hello-world
docker cp mysite/db.sqlite3 dummy:/mnt/test/db.sqlite3
docker rm dummy
```

- Upgrade to version 0.3+ is now complete.

## [0.32] - 2022-08-21

Added a logo

## [0.31] - 2022-08-18

Bugfix for scanner scheduling.
Removed django background-tasks and set up a seperate docker-container running a cronjob connecting to /scan/ on
the webserver

### IMPORTANT Update Instructions when upgrading from a version < 0.3

Version 0.3 marks the migration of the database into a separate docker volume in preparation of launching to Docker-Hub
This update requires some extra instructions

- Migration of the database file will lead to having to manually restore the database.
- Open a terminal in the root folder of your WhoIsHomeUI installation.
- Backup the current db just to be sure `cp mysite/db.sqlite3 db_backup.sqlite3`
- Run: `docker-compose down && git pull && docker-compose up -d --build`
- When the build is finished shut down the container using `docker-compose down`
- Run: (this will create the docker volume required, put your old database in it, and remove the dummy container)

```bash
docker container create --name dummy -v whoishomeui_dbstore:/mnt/test hello-world
docker cp mysite/db.sqlite3 dummy:/mnt/test/db.sqlite3
docker rm dummy
```

- Upgrade to version 0.3 is now complete.

## [0.3] - 2022-08-18

Version 0.3 marks the migration of the database into a separate docker volume in preparation of launching to Docker-Hub
This update requires some extra instructions

### IMPORTANT Update Instructions

- Migration of the database file will lead to having to manually restore the database.
- Open a terminal in the root folder of your WhoIsHomeUI installation.
- Backup the current db just to be sure `cp mysite/db.sqlite3 db_backup.sqlite3`
- Run: `docker-compose down && git pull && docker-compose up -d --build`
- When the build is finished shut down the container using `docker-compose down`
- Run: (this will create the docker volume required, put your old database in it, and remove the dummy container)

```bash
docker container create --name dummy -v whoishomeui_dbstore:/mnt/test hello-world
docker cp mysite/db.sqlite3 dummy:/mnt/test/db.sqlite3
docker rm dummy
```

- Upgrade to version 0.3 is now complete.

### Changed

- Migrated the database to a seperate docker-volume to ensure database wont be accidentally wiped in a future update and
  prepare for docker-hub.
- Fixed a bug where no internet connection might crash the script upon update check
- Changed the docker python version to slim-buster to reduce space required.

## [0.25] - 2022-08-17

Added notifications for newly detected devices

### Update Instructions

- `git pull` & `docker-compose up -d` should be enough

## [0.24] - 2022-08-17

Timeline graph added and discord notifications in local time

### Update Instructions

- `git pull` & `docker-compose up -d` should be enough

### Added

- Timeline graph to the view_host page and ability to select time range

### Changed

- Discord & email notifications in localtime

## [0.23] - 2022-08-16

Scanner start/stop switch fixed. Bugged due to editor formatting django template code

Proper formatting for time away and time home added.

## [0.22] - 2022-08-16

Small bugfixes regarding depature notification not sending and wrongly calculated times.
Proper formatting for time away and time home added.

## [0.21] - 2022-08-16

Bugfixes introduced by Discord Notification Upgrade

### Added

- Current timezone to settings page

## [0.20] - 2022-08-16

Discord notifications added

### Update Instructions

- run `docker-compose up --build` to build the new dependencies in requirements.txt

### Added

- New models: DiscordNotificationsConfig and the relating 2 migrations
- New form on the settings page which allows setting up the discord notifications
- Docker-Compose.yml now automatically runs migrate as well to migrate new changes to the DB.

### Changed

- Switched from collapse settings to modals (feedback welcome)
- Updated readme to add a line including the discord notifications intro
- One line in settings.py for a future update which will separate the db file
- Logic in scanner_functions.py to allow sending discord notifications
- Added discord related requirements to requirements.txt

## [0.19] - 2022-08-15

### Added

- Added .env file to repo to fix bug

### Changed

- Updated readme for new instructions

## [0.18] - 2022-08-14

Minor featue added, fixed a bug related to TimeZone

### Added

- Listen port can be changed from 8000 to others by exporting an environment variable
- Application TimeZone can be changed from Europe/Amsterdam to other by exporting an environment variable

### Update Instructions

- No Special instructions

## [0.17] - 2022-07-12

Minor features added, README improved and sample screenshots to view the app before installing

### Added

- On the page network Timeline titles are now clickable and redirect to device page

### Changed

- Renamed page 'Timeline' to 'Network Timeline'
- Added instructions to README on how to start app on device boot

### Update Instructions

- No Special instructions

## [0.16] - 2022-06-19

Button to clear all hosts and docker-restart enabled

### Added

- Button to clear all new hosts at once at the home page.
- Restart: Always to docker-compose file so WhoIsHome will reboot if it crashes.

### Changed

- Github Readme file: Now shows update instructions
- Update page: Shows update instructions

## [0.15] - 2022-06-19

Fixed timeline, custom e-mail messages working and minor fixes

### Added

- Save button to change target name
- Email subjects and Message are now working. Explanation added for template tags

### Changed

- Timeline now shows last 50 entries

## [0.14] - 2022-03-28

Settings page update and bugfix

### Added

- New scanner on/off button on settings page.

### Changed

- Collapsables on settings page to make it look more neat
- Changed text 'Error Log' to 'Console Log'

### Fixed

- IP-Range end wouldn't update after saving settings (fixed)
- Scanner switch didn't properly reflect status of schedules scans (fixed)

## [0.13] - 2022-03-28

Remote update check added an small bugfix.

Please run `docker-compose up --build` once to add python-requests module to the docker container.

### Added

- Now remotely checks for update and notifies user in the menu bar.
- New update.html page that shows the user the changelog and an url to the github page.

### Changed

- Removed the login page. It was a leftover from another project.

### Fixed

- Bugfix in settings page where scanner flag wouldn't show correctly.

## [0.12] - 2022-03-12

Minor update in preparation for bigger update.

### Added

- Added a random secret key in settings.py
- Added variable current_version in settings.py and latest_version.txt to be able to update checks.

### Changed

- Typo in models.py

## [0.11] - 2022-02-17

Major rehaul for the settings page

### Added

- Scanner settings. Allows changing the scanner settings from the webapp.
- Email settings. Allows changing the email settings from the webapp.
- Error log on the settings page. The error log prints out the last 30 warnings/errors. May come in handy for
  troubleshooting at Github.

### Changed

- Typo in models.py

### Fixed

- Dockerfile changed 'FROM python:3' to 'FROM python:3-buster' to increase compatibility on raspberry platforms.
