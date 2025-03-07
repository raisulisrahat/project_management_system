#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.core.management import utils

# Generate a new secret key
secret_key = utils.get_random_secret_key()

# Write the SECRET_KEY and email configurations to the .env file
with open('.env', 'w') as env_file:
    env_file.write(f'SECRET_KEY={secret_key}\n')
    env_file.write('EMAIL_HOST=smtp.gmail.com\n')
    env_file.write('EMAIL_PORT=587\n')
    env_file.write('EMAIL_USE_TLS=True\n')
    env_file.write('EMAIL_HOST_USER=\n')  # Add email username here
    env_file.write('EMAIL_HOST_PASSWORD=\n')  # Add email password here