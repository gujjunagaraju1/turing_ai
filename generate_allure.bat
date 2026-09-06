@echo off
echo Generating Allure HTML Report...
"%~dp0tools\allure-2.29.0\bin\allure.bat" generate "%~dp0reports\allure-results" -o "%~dp0reports\allure-report" --clean
echo.
echo Allure Report generated successfully at: reports\allure-report\index.html
echo Opening report in browser...
start "" "%~dp0reports\allure-report\index.html"
pause
