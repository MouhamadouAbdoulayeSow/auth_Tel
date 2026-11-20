# Phone Number Authentication API

**Domains:** Security · Software

REST API that authenticates users by phone number with SMS one-time codes.

## Features
- Custom Django user model identified by phone number instead of username.
- Registration sends an SMS verification code through **Twilio Verify**; the account is activated only after the code is approved.
- Token authentication with Django REST Framework, issued after verification or login.
- Password reset by SMS code, and logout that revokes the token.

## Endpoints
| Method | Route | Purpose |
|---|---|---|
| POST | `/register/` | create the account and send the SMS code |
| POST | `/verify/` | check the code and return a token |
| POST | `/login/` | phone number and password login |
| POST | `/password-reset/` | send a reset code |
| POST | `/password-reset-confirm/` | check the code and set a new password |
| POST | `/logout/` | revoke the token |

## Stack
Python · Django · Django REST Framework · Token authentication · Twilio Verify

## Run locally
```bash
pip install django djangorestframework twilio
export DJANGO_SECRET_KEY=... DJANGO_DEBUG=True
export TWILIO_ACCOUNT_SID=... TWILIO_AUTH_TOKEN=... TWILIO_SERVICE_SID=...   # see .env.example
python manage.py migrate
python manage.py runserver
```
Keep the Twilio credentials and the Django `SECRET_KEY` in environment variables, never in the repository.
