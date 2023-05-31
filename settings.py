import os
from dotenv import load_dotenv

load_dotenv()

valid_email = os.getenv('valid_email')
valid_password = os.getenv('valid_password')

invalid_email = "tratata@2kota.com"
invalid_password = "12345"