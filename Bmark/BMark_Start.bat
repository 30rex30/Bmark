@echo off
REM Altera para o diretório onde este arquivo .bat está localizado.
cd /d "%~dp0"

echo Tentando executar main.py com o Python...

REM Executa o script main.py usando o interpretador python.
REM Certifique-se de que o 'python' esta no PATH do seu sistema.
python main.py

if errorlevel 1 (
    echo.
    echo ERRO: O programa Python retornou um erro (exit code %errorlevel%).
    echo.
    echo Posso tentar ajudar a diagnosticar, ou verificar se 'python' esta no seu PATH.
    pause
) else (
    echo.
    echo Execucao de main.py concluida.
)

REM Mantem a janela aberta se houver erro para que voce possa ler a mensagem.
if errorlevel 1 pause
exit /b