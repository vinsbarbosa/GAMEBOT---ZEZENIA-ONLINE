@echo off
:: Verifica se o script está rodando como Administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Iniciando ZZWalker como Administrador...
    python main.py
) else (
    echo [!] PERMISSAO NEGADA: O Zezenia exige nivel de Administrador para registrar cliques.
    echo Re-iniciando e solicitando permissao...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)
pause
