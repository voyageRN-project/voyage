class ClientData:
    def __init__(self,
                 business_contact_person: str,
                 business_contact_person_phone: str,
                 credits_bought: int):
        self.business_contact_person = business_contact_person
        self.business_contact_person_phone = business_contact_person_phone
        self.credits_bought = credits_bought
        self.credits_spent = 0
