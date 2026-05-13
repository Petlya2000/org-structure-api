from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    parent_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Unique constraint: name must be unique within the same parent
    __table_args__ = (
        UniqueConstraint('parent_id', 'name', name='unique_department_name_per_parent'),
    )

    # Relationships - fixed cascade configuration (removed delete-orphan from parent)
    parent = relationship("Department", remote_side=[id], backref="children")
    employees = relationship("Employee", back_populates="department", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Department(id={self.id}, name='{self.name}', parent_id={self.parent_id})>"