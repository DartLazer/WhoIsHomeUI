# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)

## [0.18] - 2022-08-14

Minor features added, README improved and sample screenshots to view the app before installing

### Added

- Externalized the timezone and port number via DockerCompose .env files

### Changed

- Added instructions to README on how to start app on via DockerCompose .env files

### Update Instructions

- You can create .env file for docker-compose for changing portnumber and timezones
- This installation will reset your database, please proceed accordingly

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
- Error log on the settings page. The error log prints out the last 30 warnings/errors. May come in handy for troubleshooting at Github.

### Changed

- Typo in models.py

### Fixed

- Dockerfile changed 'FROM python:3' to 'FROM python:3-buster' to increase compatibility on raspberry platforms.
