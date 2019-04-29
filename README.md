# uDBPool
数据库连接池工具

#### 主要特点
1. 配置连接池大小
2. 获取连接时，可配置重试次数
3. 获取连接时，可配置等待时间

#### 部分代码
```
# 参数配置
config = {
    ... ...
    # 连接池大小
    'DB_POOL_MAX_CONN': 2,
    # 重试的等待时间(秒)
    'TIME_WAIT': 1
}

def get_conn(self, retry=3):
    """取出一个连接"""
    try:
        return self.__pool.get_nowait()
    except:
        # 重试3次，以及等待时间
        time.sleep(config['TIME_WAIT'])
        if retry > 0:
            retry -= 1
            return self.get_conn(retry)
        else:
            raise Queue.Empty
```

#### 使用方法
```
python run.py
```
