import sqlite3
import abc

class BaseSql(object):
    '''
    所有的sql操作的基类，原则上每一张表都应该对应一个更加具体的此类的子类
    这个类不应该被实例化，之后继承的类必须要实现，同时，子类必须包含以下方法：
    CreateTable：实现数据表的自动创建，无返回值
    SelectTableByxxx：实现使用指定的字段查询数据表的一行或者几行
    InsertTable：实现数据表的插入，应该把字段显式地写在参数列表中
    DeleteTableByxxx：实现使用指定的字段删除数据表的一行或者几行
    UpdateTableByxxx：实现根据某个特定的字段修改指定的数据行，修改的字段应该显式地写进参数
    此外，还应根据子类的实际用途，设计更加针对性的方法实现指定的操作
    '''
    def __init__(self, DataBaseName=None):
        if not DataBaseName:
            DataBaseName = "basedata.db"
        self._DataBaseName = DataBaseName
        self._conn = sqlite3.connect(self._DataBaseName, check_same_thread=False)
        self._cur = self._conn.cursor()

    def __del__(self):
        self._conn.commit()
        self._conn.close()

    def ExecuteSingleSql(self, sql, value=None):
        '''
        执行一行特定的sql语句，这个方法对外公开
        说明：后面基于此类实现的各个类需要在这个方法的基础上封装对应的数据库结构
        :param sql: 执行的语句
        :param value: （可选）如果语句中有问号，这里可以放问号对应的元组或者元组列表
        :return: 返回sql语句的原始执行结果
        示例：
        sql.ExecuteSingleSql("create table if not exists users (name, id, sex, address)")
        sql.ExecuteSingleSql("insert into users (name, id, sex, address) values (?, ?, ?, ?)", [("zhangsan", 1, 2, 3), ("lisi", 2, 3, 4)])
        result = sql.ExecuteSingleSql("select * from users where name = ?", ("zhangsan", ))
        '''
        if isinstance(value, list) and isinstance(value[0], (list, tuple)):
            for valu in value:
                self._cur.execute(sql, valu)
            else:
                self._conn.commit()
                result = [1, self._cur.fetchall()]
        else:
            if value:
                self._cur.execute(sql, value)
            else:
                self._cur.execute(sql)
            self._conn.commit()
            result = [1, self._cur.fetchall()]
        return result