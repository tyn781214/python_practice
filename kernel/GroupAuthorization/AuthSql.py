from utils.sqliteutil.basesql import BaseSql
from dataclasses import dataclass
from enum import Enum
import datetime
import time

class AuthType(Enum):
    NONE = 0                    # 未授权（保留）
    ADMIN = 1                   # 管理员指令授权
    CDKEY = 2                   # CDKEY授权
    OTHER = 999                 # 其他（保留）

@dataclass
class AuthTable:
    groupid: str = None         # 群号
    lastauth: int = None        # 最后一次授权的时间，时间戳
    deadline: int = None        # 到期时间
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
            DEADLINE    CHAR(25),
            TYPE        CHAR(20),
            NOTE        CHAR(50)
        )
        '''.strip()

        super().ExecuteSingleSql(sql=sql)

    def InsertTable(self, group):

        sql = '''
        INSERT INTO group_auth (GROUPID)
        VALUES (?)
        '''

        super().ExecuteSingleSql(sql, (group, ))

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

        if ret[1] is not None:
            dt_object = datetime.datetime.strptime(ret[1], '%Y-%m-%d %H:%M:%S')
            timestamp = dt_object.timestamp()
            info.lastauth = timestamp

        if ret[2] is not None:  # 处理 DEADLINE 字段
            dt_object = datetime.datetime.strptime(ret[2], '%Y-%m-%d %H:%M:%S')
            timestamp = dt_object.timestamp()
            info.deadline = timestamp

        if ret[3] is not None:
            info.type = AuthType[ret[3]].value

        info.note = ret[4]

        return info

    def UpdateTableByGroup(self, data: AuthTable):
        update = []

        if None == data.groupid:
            raise TypeError("Group cannot be None")
        if None != data.lastauth:
            dt_object = datetime.datetime.fromtimestamp(data.lastauth)
            lastauth_str = dt_object.strftime('%Y-%m-%d %H:%M:%S')
            update.append(('LASTAUTH', lastauth_str, data.groupid))
        if None != data.type:
            type_str = AuthType(data.type).name
            update.append(('TYPE', type_str, data.groupid))
        if None != data.note:
            update.append(('NOTE', data.note, data.groupid))
        if data.deadline is not None:
            dt_object = datetime.datetime.fromtimestamp(data.deadline)
            deadline_str = dt_object.strftime('%Y-%m-%d %H:%M:%S')
            update.append(('DEADLINE', deadline_str, data.groupid))

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

        data.lastauth = now
        if data.deadline is not None:
            data.deadline = datetime.datetime.fromtimestamp(data.deadline) + datetime.timedelta(days=length)
        else:
            data.deadline = datetime.datetime.fromtimestamp(now) + datetime.timedelta(days=length)
        data.deadline = data.deadline.timestamp()
        data.type = type
        data.note = note

        self.UpdateTableByGroup(data)

        return


# if __name__ == '__main__':
#     # 创建 AuthSql 对象
#     auth_sql = AuthSql()
#
#     # 测试 InsertTable 方法
#     auth_sql.InsertTable(1001)  # 使用整数型的groupid
#     auth_sql.InsertTable(1002)
#
#     # 测试 SelectTableByGroup 方法
#     info1 = auth_sql.SelectTableByGroup(1001)
#     info2 = auth_sql.SelectTableByGroup(1002)
#
#     # 打印查询结果
#     print(info1)
#     print(info2)
#
#     # 测试 DoSingleAuth 方法
#     auth_sql.DoSingleAuth(1001, 7, AuthType.ADMIN, "Test admin auth")
#     auth_sql.DoSingleAuth(1002, 15, AuthType.CDKEY, "Test cdkey auth")
#
#     # 重新查询并打印结果
#     info1_updated = auth_sql.SelectTableByGroup(1001)
#     info2_updated = auth_sql.SelectTableByGroup(1002)
#     print(info1_updated)
#     print(info2_updated)
#
#     # 测试 UpdateTableByGroup 方法
#     info1_updated.note = "Updated admin auth"
#     auth_sql.UpdateTableByGroup(info1_updated)
#
#     # 重新查询并打印结果
#     info1_updated = auth_sql.SelectTableByGroup(1001)
#     print(info1_updated)
#
#     # 测试 DeleteTableByGroup 方法
#     auth_sql.DeleteTableByGroup(1002)
#
#     # 重新查询并打印结果
#     info2_deleted = auth_sql.SelectTableByGroup(1002)
#     print(info2_deleted)



