from sqlalchemy import create_engine, func, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 连接数据库的数据
HOSTNAME = '127.0.0.1'
PORT = '3306'
DATABASE = 'hf_websocket'
USERNAME = 'root'
PASSWORD = 'mysql'

DB_URL = "mysql+pymysql://{name}:{password}@{host}:{port}/{database}?charset=utf8".format(name=USERNAME,
                                                                                          password=PASSWORD,
                                                                                          host=HOSTNAME,
                                                                                          port=PORT,
                                                                                          database=DATABASE)
# engine
engine = create_engine(DB_URL, echo=False)
# sessionmaker生成一个session类
Session = sessionmaker(bind=engine)
dbSession = Session()
Model = declarative_base(engine)


class Base(Model):
    __abstract__ = True

    @classmethod
    def all(cls):
        return dbSession.query(cls).all()

    @classmethod
    def by_id(cls, id):
        return dbSession.query(cls).filter_by(id=id).first()

    @classmethod
    def by_name(cls, name):
        return dbSession.query(cls).filter_by(name=name).first()

    @classmethod
    def get(cls, **kwargs):
        return dbSession.query(cls).filter_by(**kwargs).first()

    @classmethod
    def filter(cls, **kwargs):
        return dbSession.query(cls).filter_by(**kwargs)

    @classmethod
    def slice(cls, start, stop, **kwargs):
        """
        切片
        :param start:
        :param stop:
        :param kwargs:
        :return:
        """
        return dbSession.query(cls).filter_by(**kwargs).slice(start, stop)

    @classmethod
    def limit(cls, limit, **kwargs):
        """
        限制返回条数
        :param limit:返回几条
        :param kwargs:
        :return:
        """
        return dbSession.query(cls).filter_by(**kwargs).limit(limit)

    @classmethod
    def offset(cls, start, **kwargs):
        """
        限制从第几条开始返回
        :param start:
        :param kwargs:
        :return:
        """
        return dbSession.query(cls).filter_by(**kwargs).offset(start)

    def create(self):
        dbSession.add(self)
        dbSession.commit()

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.create()

    def save(self):
        dbSession.commit()

    @classmethod
    def count(cls):
        # 仅统计总数
        return func.count(inspect(cls).primary_key[0]).scalar()

    def delete(self):
        dbSession.query(self.__class__).filter_by(id=self.id).delete()
        dbSession.commit()
