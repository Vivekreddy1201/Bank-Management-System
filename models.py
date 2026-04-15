from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal
from typing import Optional

class User(BaseModel):
    user_id: int
    name: str
    email: str
    password: str
    created_at: Optional[datetime] = None

class Account(BaseModel):
    account_id: int
    account_no: Optional[int] = None
    user_id: int
    type: str
    balance: Decimal
    created_at: Optional[datetime] = None

class Transaction(BaseModel):
    txn_id: int
    account_id: int
    type: str
    amount: Decimal
    timestamp: Optional[datetime] = None
    remarks: Optional[str] = None
    txn_ref: Optional[str] = None

