import hashlib
import uuid
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user_name = Column(String(6420), unique=True)
    password = Column(String(128))
    token = Column(String(128))

    def __repr__(self):
        return "<User(name='%s', password='%s', token='%s')>" % (
            self.user_name, self.password, self.token)


class UserService:

    def __init__(self):
        self.engine = sqlalchemy.create_engine('sqlite:///chess.db')
        if not self.engine.dialect.has_table(self.engine, "users"):
            Base.metadata.create_all(self.engine)

    def verify_token(self, token):
        session = sessionmaker(bind=self.engine)()
        return session.query(User).filter_by(token=token).first() is not None

    def login(self, user_name, password):
        session = sessionmaker(bind=self.engine)()
        return session.query(User).filter_by(user_name=user_name, password=self.get_encode_pwd(password)).first()

    def register(self, user_name, password):
        session = sessionmaker(bind=self.engine)()
        user = User(user_name=user_name, password=self.get_encode_pwd(password), token=str(uuid.uuid1()))
        session.add(user)
        # session.add_all(
        #     [User(name='admin', password='foobar'),
        #      User(name='admin001', password='xxg527'),
        #      User(name='admin002', password='blah')]
        # )
        session.commit()
        return user

    def get_encode_pwd(self, password):
        hl = hashlib.md5()
        hl.update(password.encode(encoding='utf-8'))
        return hl.hexdigest()
