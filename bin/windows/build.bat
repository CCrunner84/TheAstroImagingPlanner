@REM .\venv\Scripts\pyinstaller.exe --distpath .\dist --noconfirm main-windows-onefile.spec
git log -n 1 --pretty=format:"%%H" > git.hash
.\venv\Scripts\create-version-file.exe .\metadata.yml --outfile file_version_info.txt

.\venv\Scripts\pyinstaller.exe --distpath .\dist --noconfirm main-windows.spec

"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" .\aip_new.iss
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" .\aip_update.iss