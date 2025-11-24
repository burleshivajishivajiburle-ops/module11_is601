# app/models/user.py
"""
User Model

This module defines the User model which represents users in the system.
Each user can have multiple calculations associated with them.
"""

from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    """
    User model representing a user in the system.
    
    A user can create and own multiple calculations. This model uses UUID
    for the primary key to ensure uniqueness across distributed systems.
    
    Attributes:
        id: Unique identifier for the user (UUID)
        username: Unique username for the user
        email: User's email address
        created_at: Timestamp when the user was created
        updated_at: Timestamp when the user was last updated
        calculations: Relationship to all calculations owned by this user
    """
    __tablename__ = 'users'

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )

    username = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    email = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationship to calculations. Passive deletes let the database enforce
    # referential integrity without forcing every calculation to belong to a user.
    calculations = relationship(
        "Calculation",
        back_populates="user",
        passive_deletes=True
    )

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email})>"
