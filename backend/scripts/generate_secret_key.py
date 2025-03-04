#!/usr/bin/env python
"""
Script to generate a secure secret key for JWT authentication.

This script generates a secure random string that can be used as a SECRET_KEY
for JWT token generation and validation.

Usage:
    python scripts/generate_secret_key.py
"""

import secrets


def generate_secret_key() -> str:
    """
    Generate a secure secret key.
    
    Returns:
        str: A secure random string suitable for use as a SECRET_KEY
    """
    return secrets.token_urlsafe(32)


if __name__ == "__main__":
    secret_key = generate_secret_key()
    print("\nGenerated SECRET_KEY:")
    print("---------------------")
    print(secret_key)
    print("\nAdd this to your .env file or environment variables:")
    print("SECRET_KEY=\"{}\"".format(secret_key))
    print("\nFor production environments, set this as an environment variable rather than in a .env file.") 