from pydantic import BaseModel, EmailStr, Field, field_validator
import re

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(UserLogin):
    name: str = Field(..., min_length=1)

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must have 8+ chars, with upper, lower, digit & special char.")
        if not re.search(r'[A-Z]', v):
            raise ValueError("Password must have 8+ chars, with upper, lower, digit & special char.")
        if not re.search(r'[a-z]', v):
            raise ValueError("Password must have 8+ chars, with upper, lower, digit & special char.")
        if not re.search(r'\d', v):
            raise ValueError("Password must have 8+ chars, with upper, lower, digit & special char.")
        if not re.search(r'[\W_]', v):
            raise ValueError("Password must have 8+ chars, with upper, lower, digit & special char.")
        return v

class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str

    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must have 8+ chars, with upper, lower, digit & special char.")
        if not re.search(r'[A-Z]', v):
            raise ValueError("Password must have 8+ chars, with upper, lower, digit & special char.")
        if not re.search(r'[a-z]', v):
            raise ValueError("Password must have 8+ chars, with upper, lower, digit & special char.")
        if not re.search(r'\d', v):
            raise ValueError("Password must have 8+ chars, with upper, lower, digit & special char.")
        if not re.search(r'[\W_]', v):
            raise ValueError("Password must have 8+ chars, with upper, lower, digit & special char.")
        return v
