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
TEST_FILE="/sdcard/speed_debug_file.txt"

# 在挂载点上创建一个文件夹
usb_new_directory="$usb_mount_point"

if [ ! -e "$usb_new_directory" ]; then
	mkdir $usb_new_directory
fi

echo "debug" > "/data/debug.txt"

# 清空日志文件
> $LOG_FILE

		
md5_origin=$(md5sum $TEST_FILE | awk '{print $1}')


echo "初始md5值为" >> $LOG_FILE
echo $md5_origin >> $LOG_FILE

#拷贝后的路径
copy_file_path="$usb_new_directory/testdata"




count=1
while [ $count -le $times ]
	do

		echo $count >> $LOG_FILE

		echo "读速度："
		dd if=/dev/block/vold/public:8,1 of=/dev/null bs=1024k count=1000
		echo "写速度："
		dd if=/dev/zero of=/mnt/media_rw/39FA-17E8/testdata bs=1024k count=1000
		
		md5_new=$(md5sum $copy_file_path | awk '{print $1}')
		
		echo "当前的md5值：" >> $LOG_FILE
		echo $md5_new >> $LOG_FILE

		if [ "$md5_origin" == "$md5_new" ]; then
			echo "MD5正确." >> $LOG_FILE
		else
			echo "MD5错误." >> $LOG_FILE
		fi
		
		# 删除测试文件
		rm $copy_file_path
		sleep 3
	    ((count++))
	done
