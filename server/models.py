import json
import os
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID

from db import Session


B = declarative_base()


class Base(B):
  __abstract__ = True

  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  created_on = Column(DateTime, default=func.now())
  updated_on = Column(DateTime, default=func.now(), onupdate=func.now())

  def serialize(self):
    return {
      "id": str(self.id),
      "created_on": self.created_on.isoformat(),
      "updated_on": self.updated_on.isoformat(),
    }

Base.query = Session.query_property()


class User(Base):
  __tablename__ = "users"

  password_hash = Column(String(120), nullable=False)
  email = Column(String(80), unique=True, nullable=False, index=True)

  def serialize(self):
    return {
      **super().serialize(),
      "email": self.email,
    }

  # copied from https://github.com/maxcountryman/flask-login/blob/main/src/flask_login/mixins.py
  __hash__ = object.__hash__

  @property
  def is_active(self):
    return True

  @property
  def is_authenticated(self):
    return self.is_active

  @property
  def is_anonymous(self):
    return False

  def get_id(self):
    try:
      return str(self.id)
    except AttributeError:
      raise NotImplementedError("No `id` attribute - override `get_id`") from None


class DefaultVersion(Base): # maps a labware definition to a default labware definition variation
  __tablename__ = "default_versions"

  name = Column(String(100), nullable=False, unique=True)
  definition_id = Column(UUID(as_uuid=True), ForeignKey("labware_definitions.id"), nullable=False)
  definition = relationship("LabwareDefinition", foreign_keys=[definition_id])


class LabwareDefinition(Base): # a labware definition, can have many variations, but only one default
  __tablename__ = "labware_definitions"

  name = Column(String(100), nullable=False, unique=False)
  path = Column(String(100), nullable=False, unique=True)

  author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
  author = relationship("User", backref="labware_definitions", lazy="select")

  def __repr__(self):
    return f"LabwareDefinition(name={self.name}, path={self.path}, author_id={self.author_id})"

  def serialize(self, base_dir=None):
    data = {
      **super().serialize(),
      "name": self.name,
    }

    if base_dir is not None:
      with open(os.path.join(base_dir, self.path), "r", encoding="utf-8") as f:
        data["definition"] = json.loads(f.read())

    return data
