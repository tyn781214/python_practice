from utils.sqliteutil.basesql import BaseSql
from dataclasses import dataclass
from enum import Enum
import datetime

@dataclass
class CdkeyTable:
    cdkey: str = None           # CDKEY
    createtime: str = None      # 创建时间，为时间戳
    validatetime: int = None    # 有效期，单位为天
    value: int = None           # 面额，单位为天
    state: int = None           # 状态，表示已使用或者未使用


class CdkeyTable(BaseSql):
    def __init__(self, DataBaseName=None):
        super().__init__(DataBaseName)
        self.CreateTable()

    def CreateTable(self):
        sql = '''
        CREATE TABLE IF NOT EXISTS cdkeys (
            cdkey TEXT PRIMARY KEY,
            createtime TEXT,
            validatetime INTEGER,
            value INTEGER,
            state INTEGER
        )
        '''
        self.ExecuteSingleSql(sql)

    def InsertTable(self, cdkey: str, validatetime: int, value: int):
        if not all([cdkey, validatetime, value]):
            raise TypeError("All parameters must be provided.")

        createtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        sql = '''
        INSERT INTO cdkeys (cdkey, createtime, validatetime, value, state)
        VALUES (?, ?, ?, ?, ?)
        '''
        self.ExecuteSingleSql(sql, (cdkey, createtime, validatetime, value, 0))

    def SelectCdkeyByCdkey(self, cdkey: str):
        if not cdkey:
            raise TypeError("Invalid input. 'cdkey' must be provided.")

        sql = '''
        SELECT * FROM cdkeys WHERE cdkey = ?
        '''
        result = self.ExecuteSingleSql(sql, (cdkey,))[1]

        if result:
            cdkey_obj = CdkeyTable()
            cdkey_obj.cdkey = result[0]
            cdkey_obj.createtime = datetime.strptime(result[1], '%Y-%m-%d %H:%M:%S').timestamp()
            cdkey_obj.validatetime = result[2]
            cdkey_obj.value = result[3]
            cdkey_obj.state = result[4]
            return cdkey_obj
        else:
            return None

    def UpdateCdkeyState(self, cdkey: str, state: int):
        if not all([cdkey, state]):
            raise TypeError("Invalid input. 'cdkey' and 'state' must be provided.")

        if not isinstance(state, int):
            raise TypeError("Invalid input. 'state' must be an integer.")

        sql = '''
        UPDATE cdkeys SET state = ? WHERE cdkey = ?
        '''
        self.ExecuteSingleSql(sql, (state, cdkey))

    def DeleteCdkeyByCdkey(self, cdkey: str):
        if not cdkey:
            raise TypeError("Invalid input. 'cdkey' must be provided.")

        sql = '''
        DELETE FROM cdkeys WHERE cdkey = ?
        '''
        self.ExecuteSingleSql(sql, (cdkey,))

# if __name__ == '__main__':
