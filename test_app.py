from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Test the hash
stored_hash = "$2b$12$O8p1FmLGdlnth6U/zvxzOebKoMJft6ozXwuFg1BaD.rgHJL1Cnp8a"
test_password = "secret"

# Verify
is_valid = pwd_context.verify(test_password, stored_hash)
print(f"Password 'secret' matches hash: {is_valid}")

# Generate new hash for comparison
new_hash = pwd_context.hash("secret")
print(f"New hash for 'secret': {new_hash}")