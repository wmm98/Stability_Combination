#!/bin/sh
# catch_log.sh
EMMC_LOG=/data/emmc.log
FLAG_LOG=/data/flag.log

mv $EMMC_LOG /data/emmc_bak

#mkdir -p /mnt/media_rw/ext4_sdcard/debuglogger
setenforce 0
let loop=0;
echo "EMMC check start"| tee > $EMMC_LOG

while [ $loop -lt $1 ]
do
    loop=`expr $loop + 1`
    echo $loop | tee -a $EMMC_LOG
    date | tee -a $EMMC_LOG	
	{ time dd if=/dev/zero of=/data/test_aaa bs=1024k count=100 conv=fdatasync; } 2>> $EMMC_LOG
	{ time dd if=/data/test_aaa of=/dev/null bs=1024k count=100; } 2>> $EMMC_LOG
    #dd if=/dev/zero of=/data/test_aaa bs=1024k count=100 >> $EMMC_LOG   
    #dd if=/data/test_aaa of=/dev/null bs=1024k count=100 >> $EMMC_LOG    
    md5sum /data/test_aaa >> $EMMC_LOG
    rm /data/test_aaa
	echo $loop | tee -a $FLAG_LOG
    sleep 1
done
