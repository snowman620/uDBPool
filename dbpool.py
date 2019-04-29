#!/usr/bin/env python
# coding: utf-8
# author: wyi

import pymysql
import Queue
import time


# 参数配置
config = {
    'DB_HOST': '192.168.217.128',
    'DB_PORT': 3306,
    'DB_NAME': 'uDBPool',
    'DB_USER': 'admin',
    'DB_PASS': '123456',
    # 连接池大小
    'DB_POOL_MAX_CONN': 2,
    # 重试的等待时间(秒)
    'TIME_WAIT': 1
}


class ConnectionPool(object):
    """连接池"""
    def __init__(self):
        self.max_conn = config['DB_POOL_MAX_CONN']
        self.__pool = Queue.Queue(maxsize=self.max_conn)
        for i in range(self.max_conn):
            conn = Connection(
                host=config['DB_HOST'],
                port=config['DB_PORT'],
                db=config['DB_NAME'],
                user=config['DB_USER'],
                passwd=config['DB_PASS'],
                charset='utf8'
            )
            conn._pool = self
            self.__pool.put_nowait(conn)

    def get_conn(self, retry=3):
        """取出一个连接"""
        try:
            return self.__pool.get_nowait()
        except:
            # 重试3次
            time.sleep(config['TIME_WAIT'])
            if retry > 0:
                retry -= 1
                return self.get_conn(retry)
            else:
                raise Queue.Empty

    def put_conn(self, conn):
        """存入一个连接"""
        if not conn._pool:
            conn._pool = self
        try:
            self.__pool.put_nowait(conn)
        except:
            raise Queue.Full

    def size(self):
        """可用连接数"""
        return self.__pool.qsize()


class Connection(pymysql.connections.Connection):
    """数据库连接"""
    def __init__(self, *args, **kwargs):
        super(Connection, self).__init__(*args, **kwargs)
        self._pool = None

    def _execute(self, query, *args):
        """执行"""
        try:
            cursor = self.cursor()
            cursor.execute(query, *args)
        except pymysql.OperationalError:
            self and self.close()
            # 尝试重连
            self.connect()
            cursor.execute(query, *args)
        return cursor

    def query_all(self, query, *args):
        """查询结果集"""
        cursor = None
        try:
            cursor = self._execute(query, *args)
            return cursor.fetchall()
        finally:
            cursor and cursor.close()
            self._pool.put_conn(self)

    def query_one(self, query, *args):
        """查询单一记录"""
        cursor = None
        try:
            cursor = self._execute(query, *args)
            return cursor.fetchone()
        finally:
            cursor and cursor.close()
            self._pool.put_conn(self)

    def insert(self, query, *args):
        """插入"""
        cursor = None
        try:
            cursor = self._execute(query, *args)
            self.commit()
            row_id = cursor.lastrowid
            return row_id
        except pymysql.IntegrityError:
            self.rollback()
        finally:
            cursor and cursor.close()
            self._pool.put_conn(self)

    def update(self, query, *args):
        """修改"""
        cursor = None
        try:
            cursor = self._execute(query, *args)
            self.commit()
            row_count = cursor.rowcount
            return row_count
        except pymysql.IntegrityError:
            self.rollback()
        finally:
            cursor and cursor.close()
            self._pool.put_conn(self)
