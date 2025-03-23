from argon2 import PasswordHasher, exceptions

# Initialize Argon2 Password Hasher
ph = PasswordHasher()

# Stored hash from the database
hashed_password = "$argon2id$v=19$m=65536,t=3,p=4$Z81RGbyCCNZVAp/FydL59w$WczvSuzBqfjn9IvqYeZTBcBAO7E+b++Tn4DcQIm7x8U"

# Password to test
plain_password = "password123"

try:
    # Verify password against the stored hash
    result = ph.verify(hashed_password.strip(), plain_password)
    print(" Password verification successful!")
except exceptions.VerifyMismatchError:
    print(" Password verification failed: Incorrect password.")
except Exception as e:
    print(f" Unexpected error: {e}")
