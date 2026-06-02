from pydantic import BaseModel, EmailStr


class EmployeeCreateRequest(BaseModel):
    employee_name: str
    employee_email: EmailStr
    role: str
    department: str
    joining_date: str


class EmployeeUpdateRequest(BaseModel):
    employee_name: str
    employee_email: EmailStr
    role: str
    department: str
    joining_date: str


class EmployeeResponse(BaseModel):
    employee_id: str
    employee_name: str
    employee_email: str
    role: str
    department: str
    joining_date: str
    onboarding_status: str
