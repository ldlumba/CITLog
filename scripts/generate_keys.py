import base64

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization


def main():
    private_key = Ed25519PrivateKey.generate()
    private_raw = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_raw = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    print("CITLOG_SIGNING_PRIVATE_KEY_B64=" + base64.b64encode(private_raw).decode("ascii"))
    print("CITLOG_SIGNING_PUBLIC_KEY_B64=" + base64.b64encode(public_raw).decode("ascii"))


if __name__ == "__main__":
    main()
