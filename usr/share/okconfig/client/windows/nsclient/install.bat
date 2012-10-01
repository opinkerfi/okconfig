@echo on

net stop NSClientpp 

xcopy "%ProgramFiles%\NSclient++\*.ini" "%ProgramFiles%\NSclient++\backup\"  /i /h /y 

xcopy %0\..\%PROCESSOR_ARCHITECTURE%\*.*  "%ProgramFiles%\NSclient++\" /e /i /h /y
xcopy %0\..\datafiles\*.*  "%ProgramFiles%\NSclient++\" /e /i /h /y
cd "%ProgramFiles%\NSclient++"


"%ProgramFiles%\NSclient++\nsclient++.exe" -uninstall
"%ProgramFiles%\NSclient++\nsclient++.exe" -install

Net Start NSClientpp
