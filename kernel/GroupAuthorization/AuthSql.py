import time

from utils.sqliteutil.basesql import BaseSql
from dataclasses import dataclass
from enum import Enum
import datetime

class AuthType(Enum):
    NONE = 0                    # 未授权（保留字）
    ADMIN = 1                   # 管理员指令授权
    CDKEY = 2                   # CDKEY授权
    OTHER = 999                 # 其他（保留字）

@dataclass
class AuthTable:
    groupid: str = None         # 群号
    lastauth: int = None        # 最后一次授权的时间，使用之间字符串进行保存
    length: int = None          # 授权时长，单位为天
    type: int = None            # 授权类型，含义见AuthType
    note: str = None            # 备注

class AuthSql(BaseSql):

    def __init__(self):
        super().__init__()
        self.CreateTable()

    def CreateTable(self):
        sql = '''
        CREATE TABLE IF NOT EXISTS group_auth (
            GROUPID     INT PRIMARY KEY NOT NULL,
            LASTAUTH    CHAR(25),
            LENGTH      INT,
            TYPE        CHAR(20),
            NOTE        CHAR(50)
        )
        '''.strip()

        super().ExecuteSingleSql(sql=sql)

    def InsertTable(self, data: AuthTable):
        if None == data.groupid:
            raise TypeError("Group cannot be None")

        if None != data.lastauth:
            dt_object = datetime.datetime.fromtimestamp(data.lastauth)
            lastauth_str = dt_object.strftime('%Y-%m-%d %H:%M:%S')
        else:
            lastauth_str = None

        if None != data.type:
            type_str = AuthType(data.type).name
        else:
            type_str = None

        sql = '''
        INSERT INTO group_auth (GROUPID, LASTAUTH, LENGTH, TYPE, NOTE)
        VALUES (?, ?, ?, ?, ?)
        '''

        super().ExecuteSingleSql(sql, (data.groupid, lastauth_str, data.length, type_str, data.note))

        return

    def SelectTableByGroup(self, group):
        sql = '''
        SELECT * FROM group_auth WHERE GROUPID = ?
        '''

        ret = super().ExecuteSingleSql(sql, (group, ))[1]
        if len(ret) == 0:
            return None     # 未查到

        ret = ret[0]
        info = AuthTable(group)

        if None != ret[1]:
            dt_object = datetime.datetime.strptime(ret[1], '%Y-%m-%d %H:%M:%S')
            timestamp = dt_object.timestamp()
            info.lastauth = timestamp

        info.length = ret[2]
        info.note = ret[4]

        if None != ret[3]:
            info.type = AuthType[ret[3]].value

        return info

    def UpdateTableByGroup(self, data: AuthTable):
        update = []

        if None == data.groupid:
            raise TypeError("Group cannot be None")
        if None != data.lastauth:
            dt_object = datetime.datetime.fromtimestamp(data.lastauth)
            lastauth_str = dt_object.strftime('%Y-%m-%d %H:%M:%S')
            update.append(('LASTAUTH', lastauth_str, data.groupid))
        if None != data.length:
            update.append(('LENGTH', data.length, data.groupid))
        if None != data.type:
            type_str = AuthType(data.type).name
            update.append(('TYPE', type_str, data.groupid))
        if None != data.note:
            update.append(('NOTE', data.note, data.groupid))

        if 0 == len(update):
            return          # 未进行任何更改，直接返回

        for up in update:
            sql = f'''
            UPDATE group_auth SET {up[0]} = '{up[1]}' WHERE GROUPID = {up[2]}
            '''

            super().ExecuteSingleSql(sql)

        return

    def DeleteTableByGroup(self, group):
        if None == group:
            raise TypeError("Group cannot be None")

        sql = '''
        DELETE FROM group_auth WHERE GROUPID = ?
        '''

        super().ExecuteSingleSql(sql, (group, ))

        return

    def DoSingleAuth(self, group, length, type, note=None):
        if None == group:
            raise TypeError("Group cannot be None")

        # 如果数据库里面没有这一条，则新增一条默认的，然后进行修改
        if None == self.SelectTableByGroup(group):
            data = AuthTable(groupid=group)
            self.InsertTable(data)

        data = self.SelectTableByGroup(group)
        now = time.time()
        if None != data.lastauth:
            last = data.lastauth
            remain_auth = data.length - (datetime.datetime.utcfromtimestamp(now) - datetime.datetime.utcfromtimestamp(last)).days
            remain_auth = remain_auth if remain_auth >= 0 else 0
        else:
            remain_auth = 0

        data.lastauth = now
        data.length = length + remain_auth
        data.type = type
        data.note = note

        self.UpdateTableByGroup(data)

        return

if __name__ == '__main__':
    s = AuthSql()
    # d = AuthTable('123456', lastauth=time.time(), length=123, note="这是一条备注", type=AuthType.CDKEY)
    s.DoSingleAuth('1234567890', 5, AuthType.CDKEY, 'additional auth')

