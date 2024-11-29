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


# 挂载点路径，假设 U 盘挂载在 /mnt/usb_drive
#usb_mount_point=/mnt/media_rw/39FA-17E8
usb_mount_points=`get_cfg_value storage_flash_path`  # 替换为您的 U 盘挂载点
usb_partitions=`get_cfg_value storage_flash_partition`
usb_num=`get_cfg_value usb_num`
times=`get_cfg_value storage_stability_test_times`

# 日志文件路径
log_base_path="/sdcard/usb_speed"

if [ ! -e "$log_base_path" ]; then
	mkdir $log_base_path
fi

echo "debug" > "/data/debug.txt"


# 获取当前日期和时间， 每次拉取可以知道文件运行时间
current_date=$(date +"%Y-%m-%d %H:%M:%S")

# 将日期和时间写入日志文件
echo "$current_date" >> "$log_file"

# 清空log文件
i=1
while [ $i -le $usb_num ]; do
	log_point=$(echo "$usb_mount_points" | awk -v idx="$i" -F ";" '{print $idx}')
	log_base_name=$(echo "$log_point" | awk -F "/" '{print $NF}')
	> $log_base_path/read_write_read_$log_base_name.log
	echo "$current_date" >> $log_base_path/read_write_read_$log_base_name.log
	echo ""  >> $log_base_path/read_write_read_$log_base_name.log
	echo ""  >> $log_base_path/read_write_read_$log_base_name.log
	i=$((i + 1))
	sleep 1
done

# 获取最初的testdata MD5值
dd if=/dev/zero of=/sdcard/testdata bs=1024k count=1000
md5_origin=$(md5sum /sdcard/testdata | awk '{print $1}')


count=1
while [ $count -le $times ]
	do
		i=1
		# 循环写下读的速度
		while [ $i -le $usb_num ]; do
		
		  part=$(echo "$usb_partitions" | awk -v idx="$i" -F ";" '{print $idx}')
		  point=$(echo "$usb_mount_points" | awk -v idx="$i" -F ";" '{print $idx}')
		  log_base_name=$(echo "$point" | awk -F "/" '{print $NF}')
		  log_name=$log_base_path/read_write_read_$log_base_name.log
		  echo $log_name
		  echo "*******************第$count次*******************" >> $log_name
		  
		  echo "读速度：" >> $log_name
		  { time dd if=$part of=/dev/null bs=1024k count=1000; } 2>> "$log_name"
		  sleep 1
		  echo "写速度：" >> $log_name
		  { time dd if=/dev/zero of=$point/testdata bs=1024k count=1000; } 2>> "$log_name"
		  
		  # 判断MD5值
		  md5_new=$(md5sum $point/testdata | awk '{print $1}')
		  echo "当前MD5值为： $md5_new" >> $log_name

		  if [ "$md5_origin" == "$md5_new" ]; then
			echo "MD5正确." >> $log_name
		  else
			echo "MD5错误." >> $log_name
		  fi
		  
		  echo "*****************************************" >> $log_name
		  
		  rm $point/testdata
		  i=$((i + 1))
		  sleep 1
		  
		done
	    ((count++))		
		sleep 3	
	done
	
# 删除辅助数据
rm /sdcard/testdata
rm $INI_FILE
rm /data/debug.txt
