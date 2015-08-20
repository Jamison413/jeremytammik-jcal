@echo off
rem to define preprocessor symbols, call with 'jcal -Dall'

set y=2012
set month=1112

set dir=C:/j/doc/pcal
if %1.==eps. goto eps
if %1.==epsview. goto epsview
if %1.==-?. goto usage
if %1.==-h. goto usage
if %1.==help. goto usage
rem if %2.==. goto usage
goto html

:html
if not %1.==. set y=%1
rem
rem version 1:
rem pcal -f %dir%/calendar -H %1 %2 %3 %4 %5 %6 %7 %8 %9 >%dir%/%2-%1.htm
rem start %dir%\%2-%1.htm
rem

rem
rem version 2, jump to month link:
rem pcal -f %dir%/calendar -H %y% >%dir%/%y%.htm
rem "C:\Program Files\Internet Explorer\IEXPLORE.EXE" file:%dir%/%y%.htm#_%month%
rem

echo s/body bgcolor="#ffffff"/body bgcolor="#ffffff" onload="window.location.href = '#_%month%'"/>C:\tmp\jcal$.sed
rem cat C:\tmp\jcal$.sed
sed -f C:/j/bat/unisodate.sed < C:\j\doc\pcal\calendar.txt > C:\j\doc\pcal\calendar
pcal -f %dir%/calendar -H %y% | sed -f C:\tmp\jcal$.sed >%dir%/%y%.htm
echo pcal done

net share | grep pcal > nul
if not errorlevel 1 goto share_exists
rem net share pcal=%dir% /users:1 /r:"This folder is temporarily shared."
net share pcal=%dir% /unlimited /remark:"This folder is temporarily shared." /cache:None

:share_exists
echo share exists
if not exist \\%computername%\pcal\%y%.htm goto share_inaccessible
start \\%computername%\pcal\%y%.htm
goto exit

:share_inaccessible
echo share inaccessible
%dir%/%y%.htm
goto exit

:eps
shift
pcal -f %dir%/calendar %1 %2 %3 %4 %5 %6 %7 %8 %9 >%dir%/%2-%1.eps
goto exit

:epsview
shift
pcal -f %dir%/calendar %1 %2 %3 %4 %5 %6 %7 %8 %9 >%dir%/%2-%1.eps
C:\bin\ghostgum\gsview\gsview32.exe /e %dir%/%2-%1.eps
goto exit

:usage
echo usage: jcal [eps,epsview] [MM] YYYY

:exit
