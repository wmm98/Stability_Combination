import pytest
from Common import log, config, process_shell
import shutil
import datetime
import configparser

if __name__ == '__main__':
    shell = process_shell.Shell()
    debug_log = log.MyLog()
    conf = config.Config()
    bg_config = configparser.ConfigParser()
    bg_config.read(conf.bg_config_ini_path)

    # bg_config = configf(configf.ui_config_file_path)
    # ui_config = configf(configf.background_config_file_path)

    ui_config = configparser.ConfigParser()
    ui_config.read(conf.ui_config_ini_path)

    xml_report_path = conf.xml_report_path
    html_report_path = conf.html_report_path
    pro_path = conf.environment_properties_path

    env_path = pro_path
    shutil.copy(env_path, xml_report_path)

    allure_list = '--allure-features=%s' % ui_config.get(conf.section_ui_to_background, conf.ui_option_cases)
    args = ['-s', '-q', '--alluredir', xml_report_path, allure_list]

    debug_log.info('当前测试集：%s' % allure_list)
    curr_time = datetime.datetime.now()
    debug_log.info('用例运行开始时间: %s' % curr_time)
    pytest.main(args)
    cmd = 'allure generate %s -o %s --clean' % (xml_report_path, html_report_path)
    try:
        shell.invoke(cmd)
    except Exception:
        debug_log.error('@@@执行失败， 请检查环境配置！！！')
        raise

    # 打开报告
    end_time = datetime.datetime.now()
    testpreiod = end_time - curr_time
    debug_log.info('用例运行结束时间: %s' % end_time)
    debug_log.info('总耗时为: %s' % testpreiod)
