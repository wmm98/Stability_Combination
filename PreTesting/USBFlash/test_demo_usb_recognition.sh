#!/system/bin/sh
# 测试前准备工作

echo "debug" > "/data/debug.txt"


# 获取ini文件的数据
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

system=`get_cfg_value system`
usb_path=`get_cfg_value usb_flash_path`
usb_test_times=`get_cfg_value usb_recognition_test_duration`
usb_dir=`get_cfg_value usb_flash_name`
usb_name=`get_cfg_value usb_flash_base_name`

echo "系统类型为：$system"
echo "$usb_path"
echo "$usb_name"
echo "$usb_dir"


# 设置初始变量
flag=0
usb_result="/sdcard/usb_result.txt"
write_data_txt="usb_write_in.txt"

# 清空 usb_result 文件
echo "" > "$usb_result"

echo "调试开始" > "$usb_path/$write_data_txt"
md5_origin=$(md5sum $usb_path/$write_data_txt | awk '{print $1}')
cat "$usb_path/$write_data_txt" >> "$usb_result"


# 开始循环
while true; do
    flag=$((flag + 1))
	echo "*********$flag*************"
	
    # 检测U盘插入
    while true; do
		echo "*********$flag*************"
        usb_content=$(ls $usb_dir 2>/dev/null)  # 对ls命令的结果进行捕获
		echo "*****$usb_content"
        if [[ "$usb_content" == *"$usb_name"* ]]; then
            cur_time=$(date +'%Y-%m-%d %H:%M:%S.%3N')
            echo "$cur_time: U盘插入$flag次" >> "$usb_result"
			
			# 判断MD5值是否正确
			md5_new=$(md5sum $usb_path/$write_data_txt | awk '{print $1}')
			echo "$md5_origin" >> "$usb_result"
			
			# 检查md5值
			if [ "$md5_origin" == "$md5_new" ]; then
					echo "MD5正确." >> "$usb_result"
				else
					echo "MD5错误." >> "$usb_result"
			fi
			
            # 写入数据
            echo "$flag@@@" >> "$usb_path/$write_data_txt"  # 写入数据
			
			
			
            # 查询写入是否成功
            usb_text=$(cat "$usb_path/$write_data_txt" 2>/dev/null)
            if [[ "$usb_text" == *"$flag@@@"* ]]; then
                cur_success_write_time=$(date +'%Y-%m-%d %H:%M:%S.%3N')
                echo "$cur_success_write_time: 写入成功$flag次" >> "$usb_result"
				# 重新赋值MD5值
				md5_origin=$(md5sum $usb_path/$write_data_txt | awk '{print $1}')
				# cat "$usb_path/$write_data_txt" >> "$usb_result"
            else
                cur_fail_write_time=$(date +'%Y-%m-%d %H:%M:%S.%3N')
                echo "$cur_fail_write_time: 写入失败$flag次" >> "$usb_result"
            fi
            break
        fi
		
        sleep 1  # 等待 0.1 秒
    done
	
	
	
	
	# 检测U盘断开
    while true; do
        #if [[ -z "$(ls /mnt/media_rw 2>/dev/null)" ]]; then
		usb_content=$(ls $usb_dir 2>/dev/null)  # 对ls命令的结果进行捕获
		if [[ -z "$usb_content" ]] || [[ ! "$usb_content" == *"$usb_name"* ]]; then
            cur_time=$(date +'%Y-%m-%d %H:%M:%S.%3N')
            echo "$cur_time: U盘断开$flag次" >> "$usb_result"
            break
        fi
        sleep 1  # 等待 0.1 秒
    done
	
	
	sleep 1
	
	echo "***********压测$flag次******" >> "$usb_result"
done

