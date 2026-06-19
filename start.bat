@echo off
echo Iniciando Sistema Pizza con Docker...
echo ==============================================
docker compose up --build -d

echo.
echo Esperando a que el servidor web se levante (10 segundos)...
timeout /t 10 /nobreak >nul

echo.
echo Cargando datos de prueba (Demo)...
docker compose exec web flask demo-seed

echo.
echo ==============================================
echo ¡TODO LISTO! 
echo Abre tu navegador en: http://localhost:5000
echo Usuario: admin
echo Clave:   Demo123!
echo ==============================================
pause
