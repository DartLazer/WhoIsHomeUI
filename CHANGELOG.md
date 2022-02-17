# Change Log
All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
 
## [0.1.1] - 2022-02-17
 
Major rehaul for the settings page
 
### Added
- Scanner settings. Allows changing the scanner settings from the webapp.
- Email settings. Allows changing the email settings from the webapp.
- Error log on the settings page. The error log prints out the last 30 warnings/errors. May come in handy for troubleshooting at Github.
 
### Changed
 - Typo in models.py
### Fixed
 - Dockerfile changed 'FROM python:3' to 'FROM python:3-buster' to increase compatibility on raspberry platforms.
