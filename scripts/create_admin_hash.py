import getpass
import sys

from werkzeug.security import generate_password_hash


def main():
    username = input("Admin username: ").strip().lower()
    display_name = input("Display name: ").strip()
    role = input("Role [admin/super_admin/viewer]: ").strip() or "admin"
    password = getpass.getpass("Password: ")
    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        print("Passwords do not match.", file=sys.stderr)
        raise SystemExit(1)
    password_hash = generate_password_hash(password, method="scrypt")
    print("\nInsert this row into public.admin_users:")
    print(f"username: {username}")
    print(f"display_name: {display_name}")
    print(f"role: {role}")
    print(f"password_hash: {password_hash}")


if __name__ == "__main__":
    main()
