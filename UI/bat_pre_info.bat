cd /d %~dp0
setlocal EnableDelayedExpansion

:: 删除原来的虚拟环境，使用公共的虚拟换
set ORIGN_VENV=poetry_venv
if exist "%ORIGN_VENV%" rmdir /s /q %CD%\%ORIGN_VENV%


::获取公共的虚拟环境的名称
set "keyword=telpo-android-automation"
set "current_dir=%cd%"
for %%G in ("%current_dir%\..\..\..\poetry_venv") do set "parent_dir=%%~fG"

for /d %%a in ("%parent_dir%\*%keyword%*") do (
    set "ENV_FOLDER_NAME=%%~nxa"
    echo Folder in parent directory containing keyword "%keyword%": !ENV_FOLDER_NAME!
)

:: 激活虚拟环境
set "PUBLIC_ENV=..\..\..\poetry_venv\!ENV_FOLDER_NAME!"
echo Folder NAME: %PUBLIC_ENV%

call %PUBLIC_ENV%\Scripts\activate
:: 返回项目更目录
::cd ..
:: 执行 Python 脚本
::python run.py
poetry run python -m pre_info

:: 退出虚拟环境
deactivate

pause

