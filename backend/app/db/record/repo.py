"""Record repository."""

from typing import Optional

from app.db.crud import CRUD
from app.db.record.models import RecordModel
from app.db.sqlalchemy import AsyncSession
from app.schemas.record import Record, RecordCreate, RecordUpdate


class RecordRepo:
    def __init__(self, session: AsyncSession):
        """Initialize repo with CRUD."""
        self._crud = CRUD(cls_model=RecordModel, session=session)

    async def create(self, record_in: RecordCreate) -> Record:
        """
        Create a new record.
        
        Args:
            record_in: Record creation data (Pydantic model)
            
        Returns:
            Created record
        """
        model_data = record_in.model_dump()
        record_id = await self._crud.create(model_data=model_data)
        record_in_db = await self._crud.get(pkey_val=record_id[0])
        return Record.from_orm(record_in_db)

    async def update(self, record_id: int, record_in: RecordUpdate) -> Record:
        """
        Update a record.
        
        Args:
            record_id: ID of the record to update
            record_in: Record update data (Pydantic model)
            
        Returns:
            Updated record
        """
        model_data = record_in.model_dump()
        await self._crud.update(
            pkey_val=record_id,
            model_data=model_data,
        )
        record_in_db = await self._crud.get(pkey_val=record_id)
        return Record.from_orm(record_in_db)

    async def delete(self, record_id: int) -> None:
        """
        Delete a record.
        
        Args:
            record_id: ID of the record to delete
        """
        await self._crud.delete(pkey_val=record_id)

    async def get(self, record_id: int) -> Record:
        """
        Get a record by ID.
        
        Args:
            record_id: ID of the record to get
            
        Returns:
            Record
        """
        record = await self._crud.get(pkey_val=record_id)
        return Record.from_orm(record)

    async def get_or_none(self, record_id: int) -> Optional[Record]:
        """
        Get a record by ID or None if not found.
        
        Args:
            record_id: ID of the record to get
            
        Returns:
            Record or None
        """
        record = await self._crud.get_or_none(pkey_val=record_id)
        if record:
            return Record.from_orm(record)

        return None

    async def get_all(self) -> list[Record]:
        """
        Get all records.
        
        Returns:
            List of records
        """
        records_in_db = await self._crud.all()
        return [Record.from_orm(record) for record in records_in_db]

    async def filter_by_record_data(self, record_data: str) -> list[Record]:
        """
        Get records filtered by record_data.
        
        Args:
            record_data: Data to filter by
            
        Returns:
            List of matching records
        """
        records_in_db = await self._crud.get_by_field(
            field="record_data",
            field_value=record_data,
        )
        return [Record.from_orm(record) for record in records_in_db]
