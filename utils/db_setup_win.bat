#!/bin/bash

# Check if PostgreSQL is installed
if command -v psql > /dev/null 2>&1; then
    echo "PostgreSQL is already installed."
    exit 0
fi

# Update package lists
sudo apt-get update

# Install PostgreSQL
sudo apt-get install -y postgresql postgresql-contrib
@echo off
setlocal

REM Check if PostgreSQL is installed
where psql >nul 2>nul
if %errorlevel%==0 (
    echo PostgreSQL is already installed.
    exit /b 0
)

REM Download PostgreSQL installer
set "PG_VERSION=13"
set "PG_INSTALLER_URL=https://get.enterprisedb.com/postgresql/postgresql-%PG_VERSION%-windows-x64-binaries.zip"
set "PG_INSTALLER_ZIP=postgresql.zip"
curl -o %PG_INSTALLER_ZIP% %PG_INSTALLER_URL%

REM Extract the installer
tar -xf %PG_INSTALLER_ZIP%

REM Run the installer
start /wait postgresql-%PG_VERSION%-windows-x64-binaries\install-postgresql.exe --mode unattended

REM Clean up
del %PG_INSTALLER_ZIP%
rd /s /q postgresql-%PG_VERSION%-windows-x64-binaries

endlocal

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql
