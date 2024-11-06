"""
Data Access Layer (implementations)
"""
from core import models
from infrastructure.db.dal import SqlAlchemyAsyncDAL
from infrastructure.db.dal import SqlAlchemyDAL


class UserDAL(SqlAlchemyDAL[models.User]):
    class Config:
        model = models.User


class UserAsyncDAL(SqlAlchemyAsyncDAL):
    class Config:
        model = models.User
