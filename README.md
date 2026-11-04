# Coderr

Coderr is the REST API backend for a freelance service marketplace. Business users
can publish service offers, and customers can place orders and leave reviews.
The project is built with Django and Django REST Framework and uses SQLite for
local development. A frontend is not included in this repository.

## Features

- Registration and login with token authentication.
- Customer and business profiles.
- Service offers with basic, standard, and premium packages.
- Order creation, status updates, and order counts.
- Reviews and platform statistics.
- Interactive API documentation with Swagger UI and ReDoc.

## Requirements

- Python 3.12 or newer. The existing development environment uses Python 3.14.
- Git.
- A terminal: PowerShell on Windows or Terminal on macOS.

SQLite is included with Python; no separate database server is required.

## Installation on Windows

Install Python from [python.org](https://www.python.org/downloads/windows/) and
Git from [git-scm.com](https://git-scm.com/downloads/win). Enable **Add Python to
PATH** in the Python installer, then open a new PowerShell window.

### 1. Clone the repository

```powershell
git clone https://github.com/FranziskaKalloch/Coderr.git
cd Coderr
```

### 2. Create and activate a virtual environment

```powershell
py -3 --version
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Check that the reported Python version is at least 3.12. If several Python
versions are installed, select one explicitly, for example `py -3.14 -m venv .venv`.

If PowerShell blocks activation, allow scripts for the current terminal session
and activate the environment again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configure the environment

```powershell
Copy-Item .env.example .env
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
notepad .env
```

Copy the generated key into `.env`, replacing the placeholder:

```dotenv
SECRET_KEY="your-generated-secret-key"
```

Save the file. Keep `.env` private; it is excluded from Git. If you already have
a `.env` file, edit it directly instead of overwriting it.

### 5. Initialize the database and start the server

```powershell
python manage.py migrate
python manage.py runserver
```

Open [Swagger UI](http://127.0.0.1:8000/api/docs/swagger/) to explore the API.
Stop the server with `Ctrl+C`.

## Installation on macOS

Install Python from [python.org](https://www.python.org/downloads/macos/).
Check whether Git is available:

```bash
git --version
```

If Git is missing, run `xcode-select --install` and complete the Command Line
Tools installation before continuing.

### 1. Clone the repository (macOS)

```bash
git clone https://github.com/FranziskaKalloch/Coderr.git
cd Coderr
```

### 2. Create and activate a virtual environment (macOS)

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
```

Check that `python3` is version 3.12 or newer. If it points to an older version,
use your installed version explicitly, for example `python3.14 -m venv .venv`.

### 3. Install dependencies (macOS)

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configure the environment (macOS)

```bash
cp .env.example .env
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
nano .env
```

Copy the generated key into `.env`, replacing the placeholder:

```dotenv
SECRET_KEY="your-generated-secret-key"
```

Save with `Ctrl+O`, press Enter, and exit with `Ctrl+X`. Keep `.env` private; it
is excluded from Git. If you already have a `.env` file, edit it directly instead
of overwriting it.

### 5. Initialize the database and start the server (macOS)

```bash
python manage.py migrate
python manage.py runserver
```

Open [Swagger UI](http://127.0.0.1:8000/api/docs/swagger/) to explore the API.
Stop the server with `Ctrl+C`.

## Local URLs

| Purpose | URL |
| --- | --- |

| Swagger UI | <http://127.0.0.1:8000/api/docs/swagger/>|
| ReDoc | <http://127.0.0.1:8000/api/docs/redoc/> |
| OpenAPI schema | <http://127.0.0.1:8000/api/schema/> |
| Django admin | <http://127.0.0.1:8000/admin/> |

The root URL (`/`) has no page configured. Use the documentation URLs above to
get started.

To access the admin interface, stop the server and create an administrator:

```bash
python manage.py createsuperuser
python manage.py runserver
```

## Authentication

Create an account with `POST /api/registration/` and log in with
`POST /api/login/`. See Swagger UI for the request fields. For authenticated API
requests, send the returned token in the HTTP header:

```http
Authorization: Token <your-token>
```

## Connecting the frontend

Set the frontend's API base URL to `http://127.0.0.1:8000/api/`.
Serve the frontend over HTTP, for example with VS Code Live Server.

By default, the backend permits API requests from `http://localhost:5500` and
`http://127.0.0.1:5500`. If your frontend uses a different address or port, set
the allowed origins in `.env` and restart Django:

```dotenv
CORS_ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
```

List exact origins separated by commas, without paths or trailing slashes.
CORS is enabled for `/api/` routes. The frontend should send the
`Authorization: Token <your-token>` header after login.

## Development

For later sessions, open a terminal in the repository, activate `.venv` using the
command for your operating system above, and run `python manage.py runserver`.
Run `python manage.py migrate` after pulling changes that add migrations.

Check the Django configuration:

```bash
python manage.py check
```

Run the test suite:

```bash
python manage.py test
```

Leave the virtual environment with `deactivate`.

## Project structure

| Directory | Purpose |
| --- | --- |
| `core/` | Project settings and root URL configuration |
| `user_auth_app/` | Registration and login |
| `profiles_app/` | Customer and business profiles |
| `offers_app/` | Service offers and packages |
| `orders_app/` | Orders, statuses, and counts |
| `reviews_app/` | Customer reviews |
| `platform_app/` | Platform statistics |

## Deployment

The instructions above are for local development. The current settings enable
`DEBUG` and use Django's development server. Before deploying, configure a private
secret key, set `DEBUG = False`, configure `ALLOWED_HOSTS`, and set up a production
server, static files, and media storage.
