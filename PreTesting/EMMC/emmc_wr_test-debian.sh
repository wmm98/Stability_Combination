#!/bin/sh
# catch_log.sh
EMMC_LOG=/data/emmc.log

mv $EMMC_LOG /data/emmc_bak
echo "EMMC check start"| tee > $EMMC_LOG
while true
do
    date | tee -a $EMMC_LOG
    dd if=/dev/zero of=/data/test_aaa bs=1024k count=100 >> $EMMC_LOG
    dd if=/data/test_aaa of=/dev/null bs=1024k count=100 >> $EMMC_LOG
    md5sum /data/test_aaa >> $EMMC_LOG
    rm /data/test_aaa
    sleep 1
done
