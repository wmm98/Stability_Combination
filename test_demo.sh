#!/system/bin/sh
# 测试前准备工作
dir="/sdcard/stresstestlog"

# 检查并删除目录
if [ -d "$dir" ]; then
    echo "目录存在，正在删除目录及其内容：$dir"
    rm -rf "$dir"/*
else
    echo "目录不存在：$dir，创建"
	mkdir "$dir"
fi


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
cases=`get_cfg_value cases`
test_duration=`get_cfg_value test_duration`
root_steps=`get_cfg_value root_steps`
mem_free_value=`get_cfg_value mem_free_value`
is_memtester=`get_cfg_value is_memtester`
is_stress_app_test=`get_cfg_value is_stress_app_test`
is_stress_app_switch=`get_cfg_value is_stress_app_switch`
memtester_duration=`get_cfg_value memtester_duration`
stressapptest_duration=`get_cfg_value stress_app_test_duration`
switch_stressapptest_duration=`get_cfg_value stress_app_switch_duration`


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


if [ "$is_stress_app_test" = "yes" ]; then
	echo "stressapptest测试开始"
	if [ "$new_free_value" -le 1750 ]; then
		echo $(date +"%Y-%m-%d %H:%M:%S") > /sdcard/stresstestlog/strssapptest.log
		/data/stressapptest -s "$stressapptest_duration" -M "$new_free_value" >> /sdcard/stresstestlog/strssapptest.log
	else
		remainder=$((mem_free_value % 1800))
		quotient=$((mem_free_value / 1800))
		#循环 多次次发送指令
		count=1
		while [ $count -le $quotient ]
		do
		  echo $(date +"%Y-%m-%d %H:%M:%S") > /sdcard/stresstestlog/strssapptest_$count.log
		  /data/stressapptest -s "$stressapptest_duration" -M 1750 >> /sdcard/stresstestlog/strssapptest_$count.log
		  ((count++))
		done
		echo $(date +"%Y-%m-%d %H:%M:%S") >> /sdcard/stresstestlog/strssapptest_$count.log
		/data/stressapptest -s "$stressapptest_duration" -M $remainder >> /sdcard/stresstestlog/strssapptest_$count.log
    fi
	echo "stressapptest测试结束"
fi


if [ "$is_stress_app_switch" = "yes" ]; then
	# 获取轮数
	test_times=$((switch_stressapptest_duration / 15))

	echo "stressapptest高低切换测试开始"
	if [ "$new_free_value" -le 1750 ]; then
	    t_times=1
		while [ $t_times -le $test_times ]
			do
			   echo $(date +"%Y-%m-%d %H:%M:%S") >> /sdcard/stresstestlog/strssapptest_cut.log
		       /data/stressapptest -s 10 -M "$new_free_value" >> /sdcard/stresstestlog/strssapptest_cut.log
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
			  echo $(date +"%Y-%m-%d %H:%M:%S") >> /sdcard/stresstestlog/strssapptest_cut.log
			  /data/stressapptest -s 10 -M 1750 >> /sdcard/stresstestlog/strssapptest_cut.log
			  ((count++))
			  sleep 1
			done
			echo $(date +"%Y-%m-%d %H:%M:%S") >> /sdcard/stresstestlog/strssapptest_cut.log
			/data/stressapptest -s 10 -M $remainder >> /sdcard/stresstestlog/strssapptest_cut.log
			((t_times++))
			sleep 5
		done
    fi
	echo "stressapptest高低切换测试结束"
fi


 nohup /data/memtester ${mem_size}M $memtester_duration > /sdcard/mem.log
 if [ "$is_memtester" == "yes" ]; then
	 echo "memster测试开始"
     nohup /data/memtester ${half_free_value}M "$memtester_duration" > /sdcard/mem.log
	 echo "memtester测试结束"
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
# echo "stressapptest测试开始"
# /data/stressapptest -s 10 -M 1000 >> /sdcard/stresstestlog/strssapptest.log
# sleep 5
# /data/stressapptest -s 10 -M 1000 >> /sdcard/stresstestlog/strssapptest.log
# echo "stressapptest测试完成"

# sleep 2


#echo "memster测试开始"
# nohup /data/memtester 550M 1 > /sdcard/mem.log
#echo "memtester测试完成"

