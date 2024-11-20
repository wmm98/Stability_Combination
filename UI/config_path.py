import os


class UIConfigPath:
    project_path = str(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
    # project_path = os.path.join(str(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))), "Stability")
    # print(project_path)
    background_config_file_path = os.path.join(project_path, "UI", "background_config.ini")
    ui_config_file_path = os.path.join(project_path, "UI", "ui_config.ini")
    debug_log_path = os.path.join(project_path, "Log", "Debug", "log.log")
    run_bat_path = os.path.join(project_path, "run.bat")

    # DDR,EMMC压测
    # bat_pre_info_path = "bat_pre_info.bat"
    bat_pre_info_path = os.path.join(project_path, "UI", "bat_pre_info.bat")
    bat_mem_info_path = os.path.join(project_path, "UI", "bat_mem_free.bat")
    py_pre_info_path = os.path.join(project_path, "UI", "pre_info.py")
    mem_log_path = os.path.join(project_path, "UI", "mem_log.txt")

    # 卡logo压测
    photo_path = os.path.join(project_path, "Photo")
    logo_base_path = os.path.join(photo_path, "BootLogo")
    logo_expect_path = os.path.join(logo_base_path, "Expect")
    logo_test_path = os.path.join(logo_base_path, "Test")
    logo_error_path = os.path.join(logo_base_path, "Error")
    logo_expect_screen0_path = os.path.join(logo_expect_path, "screen0", "expect.png")
    logo_expect_screen1_path = os.path.join(logo_expect_path, "screen1", "expect.png")
    logo_test_screen0_path = os.path.join(logo_expect_path, "screen0", "test.png")
    logo_test_screen1_path = os.path.join(logo_expect_path, "screen1", "test.png")
    bat_logo_stability_path = os.path.join(project_path, "UI", "bat_pre_logo.bat")
    bat_logo_wh_stability_path = os.path.join(project_path, "UI", "bat_wh_pre_logo.bat")
    # logo_take_path = os.path.join(project_path, "Photo", "BootLogo", "Logo", "Logo", "Logo.png")
    # logo_key_path = os.path.join(project_path, "Photo", "BootLogo", "Logo", "Key", "Key.png")
    # camera_key_path = os.path.join(project_path, "Photo", "BootLogo", "CameraPhoto", "Key", "Key.png")
    # camera2_key_path = os.path.join(project_path, "Photo", "BootLogo", "CameraPhoto", "Key", "Key2.png")
    # failed_logcat.txt
    adb_log_path = os.path.join(project_path, "Log", "Logcat", "failed_logcat.txt")
    # failed_image_key_path = os.path.join(project_path, "Photo", "BootLogo", "CameraPhoto", "Key", "Failed.png")

    # 摄像头压测
    bat_camera_stability_path = os.path.join(project_path, "UI", "bat_pre_camera.bat")

    camera_stability_path = os.path.join(project_path, "Photo", "CameraStability")
    camera_sta_exp_path = os.path.join(camera_stability_path, "Expect")
    camera_sta_test_path = os.path.join(camera_stability_path, "Test")
    # 预期前、后镜头默认镜头
    camera_sta_exp_front_path = os.path.join(camera_sta_exp_path, "Front")
    camera_sta_exp_rear_path = os.path.join(camera_sta_exp_path, "Rear")
    camera_sta_exp_default_path = os.path.join(camera_sta_exp_path, "Default")
    camera_sta_exp_front_photograph_path = os.path.join(camera_sta_exp_front_path, "Photograph",
                                                        "exp_front_photograph.jpg")
    camera_sta_exp_front_preview_path = os.path.join(camera_sta_exp_front_path, "PreView", "exp_front_preview.png")
    camera_sta_exp_rear_photograph_path = os.path.join(camera_sta_exp_rear_path, "Photograph",
                                                       "exp_rear_photograph.jpg")
    camera_sta_exp_rear_preview_path = os.path.join(camera_sta_exp_rear_path, "PreView", "exp_rear_preview.png")
    camera_sta_exp_default_photograph_path = os.path.join(camera_sta_exp_default_path, "Photograph",
                                                          "exp_default_photograph.jpg")
    camera_sta_exp_default_preview_path = os.path.join(camera_sta_exp_default_path, "PreView",
                                                       "exp_default_preview.png")
    # 测试前后镜头默认镜头
    camera_sta_test_front_path = os.path.join(camera_sta_test_path, "Front")
    camera_sta_test_rear_path = os.path.join(camera_sta_test_path, "Rear")
    camera_sta_test_default_path = os.path.join(camera_sta_test_path, "Default")
    camera_sta_test_front_photograph_path = os.path.join(camera_sta_test_front_path, "Photograph",
                                                         "test_front_photograph.jpg")
    camera_sta_test_front_preview_path = os.path.join(camera_sta_test_front_path, "PreView", "test_front_preview.png")
    camera_sta_test_rear_photograph_path = os.path.join(camera_sta_test_rear_path, "Photograph",
                                                        "test_rear_photograph.jpg")
    camera_sta_test_rear_preview_path = os.path.join(camera_sta_test_rear_path, "PreView", "test_rear_preview.png")
    camera_sta_test_default_photograph_path = os.path.join(camera_sta_test_default_path, "Photograph",
                                                           "test_default_photograph.jpg")
    camera_sta_test_default_preview_path = os.path.join(camera_sta_test_default_path, "PreView",
                                                        "test_default_preview.png")
    # U盘拔插压测
    bat_query_flash_path = os.path.join(project_path, "UI", "bat_query_flash.bat")
    process_usb_flash_path = os.path.join(project_path, "UI", "process_usb_flash_path.py")
    usb_recognize_log_path = os.path.join(project_path, "UI", "usb_recognize_log.txt")
    # U盘TF卡速率
    bat_query_storage_path = os.path.join(project_path, "UI", "bat_query_storage.bat")
    process_storage_flash_path = os.path.join(project_path, "UI", "process_storage_path.py")
    storage_query_log_path = os.path.join(project_path, "UI", "storage_query_log.txt")
    # 开关机U盘识别
    bat_boot_query_flash_path = os.path.join(project_path, "UI", "bat_boot_query_flash.bat")
    process_boot_usb_flash_path = os.path.join(project_path, "UI", "process_usb_path_boot.py")
    usb_boot_log_path = os.path.join(project_path, "UI", "boot_usb_query_log.txt")

    # 恢复出厂设置
    process_factory_reset_path = os.path.join(project_path, "UI", "factory_reset_ui.py")
