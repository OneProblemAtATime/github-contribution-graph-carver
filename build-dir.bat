:: Allows variable changes throughout the script
setlocal enabledelayedexpansion

:: Preliminary clean up
rem rm -rf exebuildenv :: Uncomment to get a full, clean build with a little more time
rm -rf assets\Scripts\__pycache__\

:: Make a virtual environment
python -m venv exebuildenv

:: Move required folders
copy main.py ".\exebuildenv\Scripts\"
IF exist assets (xcopy assets\* ".\exebuildenv\Scripts\assets\" /s)

:: Installed required python libraries
.\exebuildenv\Scripts\pip install -r requirements.txt

:: Include assets folder if provided
If exist ".\exebuildenv\Scripts\assets" (
    set "add_data=.\exebuildenv\Scripts\assets;assets"
    :: Build executable with pyinstaller
    .\exebuildenv\Scripts\pyinstaller --add-data !add_data! .\exebuildenv\Scripts\main.py --upx-dir=.\upx.exe -y --onedir
) else (
    :: Build executable with pyinstaller
    .\exebuildenv\Scripts\pyinstaller .\exebuildenv\Scripts\main.py --upx-dir=.\upx.exe -y --onedir
)

:: Make date & time string and create folder with that string
set foldername=%date:~-10,2%.%date:~-7,2%.%date:~-4,4%-"%time:~0,2%.%time:~3,2%.%time:~6,2%

set foldername=!foldername: =!
set foldername=!foldername:"=!

mkdir !foldername!

:: Place compiled executable in base folder
copy .\dist\main\main.exe .\!foldername!\
move ".\dist\main\_internal" .\!foldername!

:: Clean up
rm -rf build
rm -rf exebuildenv\Scripts\assets
rm -rf dist
rm main.spec