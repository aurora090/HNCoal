# -*- codeing = utf-8 -*-
# @Time : 2023/3/15 11:43
# @Author : 剑
# @File : save_log.py
# @Software : PyCharm

# 保存日志
import os
import datetime
current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
class Logger:
    def __init__(self, log_dir='./logs'):
        self.log_dir = log_dir
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def log(self, message):

        log_file = os.path.join(self.log_dir, f'log_{current_time}.txt')
        with open(log_file, 'a') as f:
            now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            f.write(now + '"***** Eval results *****"')
            f.write('\n')
            for key in sorted(message.keys()):
                line = "  %s = %s" % (key, str(message[key]))
                f.write(str(line))
                f.write('\n')


