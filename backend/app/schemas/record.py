"""Record schemas."""

from pydantic import BaseModel

from app.db.record.models import RecordModel


class RecordBase(BaseModel):
    """Base record schema."""
    record_data: str


class RecordCreate(RecordBase):
    """Schema for creating a record."""
    pass


class RecordUpdate(RecordBase):
    """Schema for updating a record."""
    pass


class Record(RecordBase):
    """Schema for a record."""
    id: int

    @classmethod
    def from_orm(cls, record: RecordModel) -> "Record":
        return cls(id=record.id, record_data=record.record_data)
