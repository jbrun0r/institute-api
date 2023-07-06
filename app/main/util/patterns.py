import re

cnpj_pattern = re.compile(r"(^\d{14}$)")
phone_number_pattern = re.compile(r"^$|^[1-9]{2}(?:[2-8]|9[1-9])[0-9]{3}[0-9]{4}$")
email_pattern = re.compile(r"^(?:[\w]+|([-_.])(?!\1))+@+(?:[\w]+|([-_.])(?!\1))(\.[\w]{2,10})+$")
date_pattern = re.compile(r"([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))")
http_status_code_pattern = re.compile(r"^[1-5][0-9]{2}$")
postal_code_pattern = re.compile(r"^\d{8}$")
password_pattern = re.compile(r"^(?=.*\d)(?=.*[A-Z])(?=.*[a-z])(?=.*[^\w\d\s:])([^\s]){8,128}$")
