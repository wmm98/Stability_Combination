#!/system/bin/sh
# 测试前准备工作
dir="/sdcard/stresstestlog"

# 检查并删除目录
stress_test_log="/data/stress_test_log"
dir="/data/stress_test_log/stresstestlog"

if [ -d "$stress_test_log" ]; then
    echo "目录存在，正在删除目录及其内容：$stress_test_log"
    rm -rf "$stress_test_log"/*
else
    echo "目录不存在：$$stress_test_log，创建"
	mkdir "$stress_test_log"
fi

sleep 2

if [ -d "$dir" ]; then
    echo "目录存在，正在删除目录及其内容：$dir"
    rm -rf "$dir"/*
else
    echo "目录不存在：$dir，创建"
	mkdir "$dir"
fi

echo "debug" > "$stress_test_log/debug.txt"


# 获取ini文件的数据
INI_FILE="/data/ui_config.ini"
INI_SECTION="UI-Background"

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
mem_free_value=`get_cfg_value mem_free_value`
is_memtester=`get_cfg_value is_memtester`
is_stress_app_test=`get_cfg_value is_stress_app_test`
is_stress_app_switch=`get_cfg_value is_stress_app_switch`
is_emmc_test=`get_cfg_value is_emmc_test`
memtester_duration=`get_cfg_value memtester_duration`
stressapptest_duration=`get_cfg_value stress_app_test_duration`
switch_stressapptest_duration=`get_cfg_value stress_app_switch_duration`
emmc_duration=`get_cfg_value emmc_duration`

echo "系统类型为：$system"

# 获取出来运行内存值
new_free_value=0
# 检查结果是否小于 10
if [ "$mem_free_value" -lt 1800 ]; then
    new_free_value=$((mem_free_value - 50))
elif [ "$mem_free_value" -eq 1800 ]; then
   new_free_value=1750
else
	new_free_value="$mem_free_value"
fi

# memtester 测试
half_free_value=$((mem_free_value / 2))

stressapptest_duration_sec=$((stressapptest_duration * 3600))

if [ "$is_stress_app_test" = "yes" ]; then
	echo "stressapptest测试开始"
	if [ "$new_free_value" -le 1750 ]; then
		echo $(date +"%Y-%m-%d %H:%M:%S") > /data/stress_test_log/stresstestlog/strssapptest.log
		/data/stressapptest -s "$stressapptest_duration_sec" -M "$new_free_value" >> /data/stress_test_log/stresstestlog/strssapptest.log
	else
		remainder=$((mem_free_value % 1800))
		quotient=$((mem_free_value / 1800))
		#循环 多次次发送指令
		count=1
		while [ $count -le $quotient ]
		do
		  echo $(date +"%Y-%m-%d %H:%M:%S") > /data/stress_test_log/stresstestlog/strssapptest_$count.log
		  /data/stressapptest -s "$stressapptest_duration" -M 1750 >> /data/stress_test_log/stresstestlog/strssapptest_$count.log
		  ((count++))
		done
		echo $(date +"%Y-%m-%d %H:%M:%S") >> /data/stress_test_log/stresstestlog/strssapptest_$count.log
		/data/stressapptest -s "$stressapptest_duration" -M $remainder >> /data/stress_test_log/stresstestlog/strssapptest_$count.log
    fi
	echo "stressapptest测试结束"
fi


if [ "$is_stress_app_switch" = "yes" ]; then
	# 获取轮数
	test_times=$((switch_stressapptest_duration * 3600 / 15))

	echo "stressapptest高低切换测试开始"
	if [ "$new_free_value" -le 1750 ]; then
	    t_times=1
		while [ $t_times -le $test_times ]
			do
			   echo $(date +"%Y-%m-%d %H:%M:%S") >> /data/stress_test_log/stresstestlog/strssapptest_cut.log
		       /data/stressapptest -s 10 -M "$new_free_value" >> /data/stress_test_log/stresstestlog/strssapptest_cut.log
			   echo "循环次数为 $t_times"
			   ((t_times++))
			   sleep 5
			done
	else
		remainder=$((mem_free_value % 1800))
		quotient=$((mem_free_value / 1800))
		echo "$quotient 条进程"
		#循环 多次次发送指令
		t_times=1
		while [ $t_times -le $test_times ]
		do
			echo "循环次数为： $t_times"
			count=1
			while [ $count -le $quotient ]
			do
			  echo $(date +"%Y-%m-%d %H:%M:%S") >> /data/stress_test_log/stresstestlog/strssapptest_cut.log
			  /data/stressapptest -s 10 -M 1750 >> /data/stress_test_log/stresstestlog/strssapptest_cut.log
			  ((count++))
			  sleep 1
			done
			echo $(date +"%Y-%m-%d %H:%M:%S") >> /data/stress_test_log/stresstestlog/strssapptest_cut.log
			/data/stressapptest -s 10 -M $remainder >> /data/stress_test_log/stresstestlog/strssapptest_cut.log
			((t_times++))
			sleep 5
		done
    fi
	echo "stressapptest高低切换测试结束"
fi


# nohup /data/memtester ${mem_size}M $memtester_duration > /sdcard/mem.log
if [ "$is_memtester" = "yes" ]; then
 echo "memster测试开始"
   nohup /data/memtester ${half_free_value}M "$memtester_duration" > /data/stress_test_log/memstertest.log
 echo "memtester测试结束"
fi

#emmc
if [ "$is_emmc_test" = "yes" ]; then
  echo "emmc测试开始"
  if [ "$system" = "Android" ]; then
	EMMC_LOG=/data/stress_test_log/emmc.log
	echo "EMMC check start" > $EMMC_LOG
    # mv $EMMC_LOG /data/emmc_bak
    #mkdir -p /mnt/media_rw/ext4_sdcard/debuglogger
    setenforce 0
    count=1
	while [ $count -le $emmc_duration ]
	do
	  echo $count >> $EMMC_LOG
	  date >> $EMMC_LOG	
	  { time dd if=/dev/zero of=/data/test_aaa bs=1024k count=100; } >> $EMMC_LOG  2>&1  
	  { time dd if=/data/test_aaa of=/dev/null bs=1024k count=100; } >> $EMMC_LOG  2>&1   
	  md5sum /data/test_aaa >> $EMMC_LOG
	  rm /data/test_aaa
	  echo "*************************" >> $EMMC_LOG
	  sleep 1
	 ((count++))
	done

   elif [ "$system" = "Linux" ]; then
	EMMC_LOG=/data/stress_test_log/emmc.log
	FLAG_LOG=/data/stress_test_log/flag.log
	echo "" > $FLAG_LOG
	setenforce 0
	echo "EMMC check start" >> $EMMC_LOG
	count=1
	while [ $count -le $emmc_duration ]
	do
		echo $count >> $EMMC_LOG
		date >> $EMMC_LOG	
		{ time dd if=/dev/zero of=/data/test_aaa bs=1024k count=100; } >> $EMMC_LOG 2>&1 
		{ time dd if=/data/test_aaa of=/dev/null bs=1024k count=100; } >> $EMMC_LOG 2>&1  
		md5sum /data/test_aaa >> $EMMC_LOG
		rm /data/test_aaa
		echo "*************************" >> $EMMC_LOG
		sleep 1
		((count++))
	done
	
   elif [ "$system" = "Debian" ]; then
	EMMC_LOG=/data/stress_test_log/emmc.log
	echo "EMMC check start" > $EMMC_LOG
	count=1
	while [ $count -le $emmc_duration ]
	do
	    echo $count >> $EMMC_LOG
		date >> $EMMC_LOG
		{ time dd if=/dev/zero of=/data/test_aaa bs=1024k count=100; } >> $EMMC_LOG 2>&1 
		{ time dd if=/data/test_aaa of=/dev/null bs=1024k count=100; }>> $EMMC_LOG  2>&1 
		md5sum /data/test_aaa >> $EMMC_LOG
		rm /data/test_aaa
		((count++))
		sleep 1
		echo "*************************" >> $EMMC_LOG
	done
   else 
	EMMC_LOG=/data/stress_test_log/emmc.log
	setenforce 0
	echo "EMMC check start" > $EMMC_LOG
	count=1
	while [ $count -le $emmc_duration ]
	do
		echo $count >> $EMMC_LOG
		date >> $EMMC_LOG	
		{ time dd if=/dev/zero of=/dev/block/platform/bootdevice/by-name/userdata bs=512k count=1 conv=fsync; } >> $EMMC_LOG 2>&1
		{ time dd if=/dev/block/platform/bootdevice/by-name/userdata of=/dev/null bs=512k count=1; } >> $EMMC_LOG 2>&1
		md5sum /dev/block/platform/bootdevice/by-name/userdata >> $EMMC_LOG 
		rm /dev/block/platform/bootdevice/by-name/userdata
		((count++))
		sleep 3
		echo "*************************" >> $EMMC_LOG
	done

  fi
fi






# 设置内部字段分隔符为逗号
#IFS=','

# 使用 for 循环逐个处理分割后的字符串部分
#for item in $cases; do
  
  #echo "Processing item: '$item'"  # 输出当前处理的项
  #if [ "$is_memtester" == "DDR-memtester" ]; then
    #echo "yes"
  #fi
#done

# 可选：重置 IFS 为默认值（通常脚本结束时会自动恢复）
#unset IFS

# touch /sdcard/strssapptest.log
echo "" > /sdcard/strssapptest.log
# echo "stressapptest测试开始"
# /data/stressapptest -s 10 -M 1000 >> /sdcard/stresstestlog/strssapptest.log
# sleep 5
# /data/stressapptest -s 10 -M 1000 >> /sdcard/stresstestlog/strssapptest.log
# echo "stressapptest测试完成"

# sleep 2


#echo "memster测试开始"
# nohup /data/memtester 550M 1 > /sdcard/mem.log
#echo "memtester测试完成"

