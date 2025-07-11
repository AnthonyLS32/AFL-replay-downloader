import keyring
import sys

SERVICE_NAME = "AFL_PW"

def store(password):
    keyring.set_password(SERVICE_NAME, "user", password)
    print("Password stored securely.")

def retrieve():
    return keyring.get_password(SERVICE_NAME, "user")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python credential_manager.py <your_afl_password>")
    else:
        store(sys.argv[1])
