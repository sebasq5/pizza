@echo off
echo.
echo  ========================================
echo    SISTEMA PIZZA - Inicio Automatico
echo  ========================================
echo.

REM Verificar que Docker esta corriendo
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker no esta corriendo.
    echo Por favor abre Docker Desktop y vuelve a intentarlo.
    pause
    exit /b 1
)

echo [1/4] Bajando contenedores anteriores si existen...
docker compose down >nul 2>&1

echo [2/4] Construyendo e iniciando contenedores...
docker compose up --build -d
if errorlevel 1 (
    echo [ERROR] Fallo al iniciar Docker. Mostrando logs...
    docker compose logs
    pause
    exit /b 1
)

echo [3/4] Esperando a que el sistema este listo...
set /a intentos=0
:wait_loop
set /a intentos+=1
if %intentos% gtr 30 (
    echo.
    echo [ERROR] El servidor no pudo arrancar a tiempo. Mostrando logs...
    docker compose logs web
    pause
    exit /b 1
)
docker compose ps web | findstr "running" >nul 2>&1
if errorlevel 1 (
    timeout /t 2 /nobreak >nul
    goto wait_loop
)

echo Esperando 5 segundos para que Flask inicialice...
timeout /t 5 /nobreak >nul

echo [4/4] Cargando datos de prueba...
docker compose exec web flask demo-seed
if errorlevel 1 (
    echo [AVISO] No se pudieron cargar datos demo ^(puede que ya existan^)
)

echo.
echo  ========================================
echo    ¡SISTEMA LISTO!
echo  ========================================
echo.
echo    Abre tu navegador en:
echo    http://localhost:5000
echo.
echo    Usuario: admin
echo    Clave:   P1zz@S3cur3!2026
echo  ========================================
echo.
start http://localhost:5000
pause
