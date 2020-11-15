from typing import Any, Type, TypeVar

from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import Session as _Session
from sqlalchemy.orm.exc import NoResultFound


@as_declarative()
class Base:
    pass


M = TypeVar('M')


class Session(_Session):
    def upsert(self, model: Type[M], **fields: Any) -> M:
        try:
            return self.query(model).filter_by(**fields).one()
        except NoResultFound:
            m = model(**fields)
            self.add(m)
            return m
