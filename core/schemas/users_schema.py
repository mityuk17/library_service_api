from pydantic import BaseModel


class UpdatedUserData(BaseModel):
    id: int
    email: str = None
    login: str = None
    password: str = None
    role: str = None
    active: bool = None


class User(BaseModel):
    id: int
    email: str
    login: str
    password_hash: str
    role: str
    active: bool

    class Config:
        orm_mode = True

    def check_role(self, required_role):
        return self.role == required_role


class NoPasswordUser(BaseModel):
    id: int
    email: str
    login: str
    role: str
    active: bool

    class Config:
        orm_mode = True


class NewUserData(BaseModel):
    email: str
    login: str
    password: str
    role: str
