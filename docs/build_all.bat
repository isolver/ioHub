call %~dp0..\..\..\env.bat
cd %~dp0

rm -r -f "%~dp0..\..\..\python-2.7.3\Lib\site-packages\iohub"
rm -r -f "%~dp0..\..\..\python-2.7.3\Lib\site-packages\psychopy"
rm -r -f "C:\Python26\Lib\site-packages\iohub"
rm -r -f "C:\Python26\Lib\site-packages\psychopy"

xcopy "%~dp0..\iohub" "%~dp0..\..\..\python-2.7.3\Lib\site-packages\iohub\" /E /H /J /EXCLUDE:xcopy_excludes.txt
xcopy "D:\DropBox\DEV\PsychoPy\psychopy\" "%~dp0..\..\..\python-2.7.3\Lib\site-packages\psychopy\" /E /H /J /EXCLUDE:xcopy_excludes.txt
xcopy "%~dp0..\iohub" "C:\Python26\Lib\site-packages\iohub\" /E /H /J /EXCLUDE:xcopy_excludes.txt
xcopy "D:\DropBox\DEV\PsychoPy\psychopy\" "C:\Python26\Lib\site-packages\psychopy\" /E /H /J /EXCLUDE:xcopy_excludes.txt

call make.bat html

PAUSE
