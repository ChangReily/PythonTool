Set PythonFile=123

C:\Python36\Scripts\pyinstaller --onefile %PythonFile%.py
Copy dist\%PythonFile%.exe 
rd /s /q build
rd /s /q dist
del %PythonFile%.spec
pause