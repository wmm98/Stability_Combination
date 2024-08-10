#!/bin/sh
# catch_log.sh
EMMC_LOG=/data/emmc.log

mv $EMMC_LOG /data/emmc_bak

#mkdir -p /mnt/media_rw/ext4_sdcard/debuglogger
setenforce 0
let loop=0;
echo "EMMC check start"| tee > $EMMC_LOG

while true
do
    loop=`expr $loop + 1`
    echo $loop | tee -a $EMMC_LOG
    date | tee -a $EMMC_LOG	
    dd if=/dev/zero of=/dev/block/platform/bootdevice/by-name/userdata bs=512k count=1 conv=fsync  | tee -a $TF_LOG   
    dd if=/dev/block/platform/bootdevice/by-name/userdata of=/dev/null bs=512k count=1 | tee -a $TF_LOG    
    md5sum /dev/block/platform/bootdevice/by-name/userdata | tee -a $EMMC_LOG
    rm /dev/block/platform/bootdevice/by-name/userdata
   
    sleep 3
done
