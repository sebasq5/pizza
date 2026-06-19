@echo off
echo Iniciando Sistema Pizza con Docker...
echo ==============================================
docker compose up --build -d

echo.
echo Esperando a que la base de datos este lista...
:wait_db
docker compose ps db | findstr "healthy" >nul 2>&1
if errorlevel 1 (
    timeout /t 3 /nobreak >nul
    goto wait_db
)

echo Base de datos lista. Esperando al servidor web...
:wait_web
docker compose ps web | findstr "running" >nul 2>&1
if errorlevel 1 (
    timeout /t 3 /nobreak >nul
    goto wait_web
)

echo Esperando 5 segundos extra para que Flask arranque...
timeout /t 5 /nobreak >nul

echo.
echo Cargando datos de prueba (Demo)...
docker compose exec web flask demo-seed

echo.
echo ==============================================
echo ¡TODO LISTO!
echo Abre tu navegador en: http://localhost:5000
echo Usuario: admin
echo Clave:   P1zz@S3cur3!2026
echo ==============================================
pause
