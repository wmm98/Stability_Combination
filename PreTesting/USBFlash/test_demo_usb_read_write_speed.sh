#!/system/bin/sh
# 测试前准备工作

INI_FILE="/data/ui_config.ini"

# 获取ini文件的数据
get_cfg_value()
{
    key=$1
    val=`grep $key $INI_FILE | sed -n "s/ *$key *= *//p" | sed -n 's/[[:space:]]*$//p'`
    if [ "$val" != "" ]; then
        echo "$val"
    else
        echo "not found"
    fi
}

# 设置源文件和目标路径
#source_file="/sdcard/usb_read_logcat.txt"  # 替换为您的源文件路径
log_file="/sdcard/storage_read_write_speed_result_log.txt"  # 设置日志文件路径

#!/bin/bash

# 挂载点路径，假设 U 盘挂载在 /mnt/usb_drive
#usb_mount_point=/mnt/media_rw/39FA-17E8
usb_mount_point=`get_cfg_value storage_flash_path`  # 替换为您的 U 盘挂载点
times=`get_cfg_value storage_stability_test_times`

# 日志文件路径
LOG_FILE="/sdcard/storage_read_write_speed_result_log.txt"

# 创建一个临时测试文件名
TEST_FILE="$usb_mount_point/test_aaa"

echo "debug" > "/data/debug.txt"

# 清空日志文件
> $LOG_FILE

count=0
while [ $count -le $times ]
	do

		echo $count >> $LOG_FILE

		# 测试写入速度
		{ time dd if=/dev/zero of=$TEST_FILE bs=1024k count=500; } >> $LOG_FILE 2>&1

		# 测试读取速度
		{ time dd if=$TEST_FILE of=/dev/null bs=1024k count=500; } >> $LOG_FILE 2>&1
		
		md5sum $TEST_FILE >> $LOG_FILE
		# 删除测试文件
		rm $TEST_FILE
		sleep 1
	    ((count++))
	done
		
		

