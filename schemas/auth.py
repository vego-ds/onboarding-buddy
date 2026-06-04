from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: str = "employee"
    tenant_id: str = "TENANT_DEFAULT"
    employee_id: str | None = None
    manager_id: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=16)


class LogoutRequest(BaseModel):
    refresh_token: str = Field(min_length=16)


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    reset_token: str = Field(min_length=16)
    new_password: str = Field(min_length=8, max_length=128)


class SSOLoginRequest(BaseModel):
    provider: str = "oidc"
    email: EmailStr
    name: str = Field(min_length=1, max_length=120)
    tenant_id: str = "TENANT_DEFAULT"
    role: str = "employee"
    provider_subject: str = Field(min_length=1, max_length=200)
    assertion: str = Field(min_length=1, max_length=5000)
