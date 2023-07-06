from flask_restx import Namespace, fields


class AddressDTO:
    api = Namespace("address", "Address related operations")

    address = api.model("Address", {
        "country": fields.String(
            max_length=80,
            description="Country",
            example="United States",
        ),
        "state": fields.String(
            required=True,
            max_length=80,
            description="State",
            example="CA",
        ),
        "city": fields.String(
            required=True,
            max_length=80,
            description="City",
            example="San Francisco",
        )
    }, strict=True)

    institute_address = api.model("InstituteAddress", {
        **address,
        "postal_code": fields.String(
            required=True,
            max_length=8,
            description="Postal code",
            example="94107",
            pattern=r"^\d{5}-?\d{0,4}$",
        ),
        "neighborhood": fields.String(
            required=True,
            max_length=80,
            description="Neighborhood",
            example="South Beach"
        ),
        "street": fields.String(
            required=True,
            max_length=80,
            description="Street",
            example="Colin P Kelly Jr St"
        ),
        "number": fields.String(
            required=True,
            max_length=255,
            description="Street number",
            example="88"
        ),
        "complement": fields.String(
            max_length=255,
            description="Address complement",
            example="crossing with the Brannan St"
        )
    }, strict=True)
