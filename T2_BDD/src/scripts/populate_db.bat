@echo off
REM Populate the database with data
REM Usage: T2_BDD\src\scripts\populate_db.bat

cd /d %~dp0..\..\..

REM Load environment variables from .env if present
if exist .env (
    for /f "usebackq tokens=1* delims==" %%A in (".env") do (
        if not "%%A"=="" set "%%A=%%B"
    )
)

if "%DB_NAME%"=="" set DB_NAME=sae5idfou
if "%DB_USER%"=="" set DB_USER=idfou

echo Populating database '%DB_NAME%'...

docker ps -q -f name=sae5db > nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Container 'sae5db' is not running. Please start it with 'docker-compose up -d'.
    exit /b 1
)

docker exec -e PGPASSWORD="%DB_ROOT_PASSWORD%" -w /app sae5db psql -U "%DB_USER%" -d "%DB_NAME%" -v ON_ERROR_STOP=1 -f T2_BDD/src/sql/populate.sql

if %errorlevel% equ 0 (
    echo Database populated successfully.
) else (
    echo Error populating database.
    exit /b 1
)
