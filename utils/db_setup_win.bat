@echo off
setlocal

REM Function to generate the .env file in the profiles directory
:generate_env_file
    echo Generating .env file...
    if not exist profiles mkdir profiles

    (    
    echo LLM_FOLDER=llm_models    
    echo COLOR_SCHEME=dark 
    echo OPEN_AI_ENABLED=false 
    echo OPEN_AI_KEY=   
    echo DB_NAME=study_stream_db
    echo DB_USER=study_stream_db_admin
    echo DB_PASSWORD=study_stream_db_psw
    echo DB_HOST=localhost
    echo DB_PORT=5432
    ) > profiles\.env

    echo .env file created with database settings in profiles directory.
    goto :eof

REM Check if PostgreSQL is installed
where psql >nul 2>nul
if %errorlevel%==0 (
    echo PostgreSQL is already installed.
    goto :generate_env_file
)

REM Set PostgreSQL version
set "PG_VERSION=13"
set "PG_INSTALLER_URL=https://get.enterprisedb.com/postgresql/postgresql-%PG_VERSION%-windows-x64-binaries.zip"
set "PG_INSTALLER_ZIP=postgresql.zip"

REM Download PostgreSQL installer
echo Downloading PostgreSQL installer...
curl -o %PG_INSTALLER_ZIP% %PG_INSTALLER_URL%

REM Extract the installer
echo Extracting PostgreSQL installer...
tar -xf %PG_INSTALLER_ZIP%

REM Run the installer
echo Running PostgreSQL installer...
start /wait postgresql-%PG_VERSION%-windows-x64-binaries\install-postgresql.exe --mode unattended

REM Clean up
echo Cleaning up...
del %PG_INSTALLER_ZIP%
rd /s /q postgresql-%PG_VERSION%-windows-x64-binaries

REM Generate .env file
:generate_env_file

REM Set environment variables for PostgreSQL from profiles\.env file
if exist profiles\.env (
    for /f "tokens=*" %%i in (profiles\.env) do set %%i
) else (
    echo .env file not found. Generating a new one.
    call :generate_env_file
    for /f "tokens=*" %%i in (profiles\.env) do set %%i
)

REM Ensure environment variables are set
if "%DB_NAME%"=="" goto :missing_env
if "%DB_USER%"=="" goto :missing_env
if "%DB_PASSWORD%"=="" goto :missing_env
if "%DB_HOST%"=="" goto :missing_env
if "%DB_PORT%"=="" goto :missing_env
goto :env_set

:missing_env
echo One or more environment variables are not set. Please check the profiles\.env file.
exit /b 1

:env_set

REM Initialize PostgreSQL cluster if not already initialized
set "PGDATA=C:\Program Files\PostgreSQL\%PG_VERSION%\data"
if not exist "%PGDATA%" (
    echo Initializing PostgreSQL cluster...
    initdb -D "%PGDATA%"
)

REM Start PostgreSQL service
net start postgresql-x64-%PG_VERSION%
if %errorlevel% neq 0 (
    echo Starting PostgreSQL service...
    sc start postgresql-x64-%PG_VERSION%
)

REM Create database and user
echo Creating database and user...
psql -U postgres -c "CREATE DATABASE %DB_NAME%;"
psql -U postgres -c "CREATE USER %DB_USER% WITH PASSWORD '%DB_PASSWORD%';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE %DB_NAME% TO %DB_USER%;"

echo PostgreSQL setup complete.
endlocal
