#!/usr/bin/env python
# coding: utf-8
# author: wyi

import threading
import Queue
from dbpool import ConnectionPool


class Task(threading.Thread):
    """模拟任务"""
    def __init__(self, p):
        super(Task, self).__init__()
        self.__pool = p

    def run(self):
        try:
            conn = self.__pool.get_conn()
            result = conn.query_all('SELECT `id`,`name` FROM `tb1`')
            print '{0}:{1}'.format(self.name, str(result[0][1]))
        except Queue.Empty:
            # 如果多次尝试还是无法获取连接，抛出Queue.Empty异常
            # do something
            print '{0}: queue empty'.format(self.name)
        except Exception as e:
            # do something
            print 'error'


if __name__ == "__main__":
    """用多线程模拟任务，使用连接池"""
    pool = ConnectionPool()

    thread_list = []

    for i in range(5):
        task = Task(pool)
        thread_list.append(task)

    for t in thread_list:
        t.setDaemon(True)
        t.start()

    for t in thread_list:
        t.join()
