from pydantic import BaseModel


class ClientData(BaseModel):
    business_contact_person: str
    business_contact_person_phone: str
    credits_bought: int
    credits_spent: int = 0
