class DataValidator:

    def validate(self):
        if not self.data:
            raise Exception("Data is empty")
        if not self.data.get("name"):
            raise Exception("Name is required")
        if not self.data.get("email"):
            raise Exception("Email is required")
        if not self.data.get("phone"):
            raise Exception("Phone is required")
        if not self.data.get("address"):
            raise Exception("Address is required")
        if not self.data.get("city"):
            raise Exception("City is required")
        if not self.data.get("state"):
            raise Exception("State is required")
        if not self.data.get("zip"):
            raise Exception("Zip is required")
        if not self.data.get("country"):
            raise Exception("Country is required")
        if not self.data.get("card_number"):
            raise Exception("Card number is required")
        if not self.data.get("card_expiry"):
            raise Exception("Card expiry is required")
        if not self.data.get("card_cvc"):
            raise Exception("Card cvc is required")
        return True