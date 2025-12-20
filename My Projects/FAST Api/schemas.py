# We need this for data validation, data serialization and deserialization
# in the place of serializer, we're using pydantic to convert the json to object and object to jason
# It's simply type conversion

from pydantic import BaseModel, EmailStr

class EmployeeBase(BaseModel):
    name: str
    email: EmailStr
    age: int
    department: str
    salary: float

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(EmployeeBase):
    pass

class EmployeeResponse(EmployeeBase):
    pass

