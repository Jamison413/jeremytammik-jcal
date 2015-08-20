@echo off
echo Creating C:\j\doc\pcal\wgcal.htm ...
sed -f C:/j/bat/unisodate.sed < C:\j\doc\pcal\wgcal.txt > C:\j\doc\pcal\wgcal
pcal -H -f C:/j/doc/pcal/wgcal 2008 > C:\j\doc\pcal\wgcal.htm
C:\j\doc\pcal\wgcal.htm
