import enum


class Type(enum.Enum):
    Sick = 1
    Maternity = 2
    Vacation = 3


class Role(enum.Enum):
    Employee = 1
    Manager = 2


class Status(enum.Enum):
    approved = 1
    pending = 2
