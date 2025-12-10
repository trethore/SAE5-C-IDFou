@echo off
REM Initialize the database schema
REM Usage: T2_BDD\src\scripts\init_db.bat

cd /d %~dp0..\..\..

REM Load environment variables from .env if present
if exist .env (
    for /f "usebackq tokens=1* delims==" %%A in (".env") do (
        if not "%%A"=="" set "%%A=%%B"
    )
)

if "%DB_NAME%"=="" set DB_NAME=sae5idfou
if "%DB_USER%"=="" set DB_USER=idfou

echo Initializing database '%DB_NAME%' with user '%DB_USER%'...

docker ps -q -f name=sae5db > nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Container 'sae5db' is not running. Please start it with 'docker-compose up -d'.
    exit /b 1
)

docker exec -e PGPASSWORD="%DB_ROOT_PASSWORD%" -w /app sae5db psql -U "%DB_USER%" -d "%DB_NAME%" -f T2_BDD/src/sql/schema.sql

if %errorlevel% equ 0 (
    echo Schema initialized successfully.
) else (
    echo Error initializing schema.
    exit /b 1
)
