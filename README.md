# SkillMapper

A minimal Python Flask app to authenticate with hh.ru (HeadHunter) via OAuth2, fetch your resumes, and retrieve recommended vacancies.

---

## Features

- OAuth2 Authorization Code flow to get access and refresh tokens
- Fetch user resumes from hh.ru API
- Retrieve recommended vacancies based on a selected resume
- Automatic token refresh support

---

## Setup

1. **Clone the repository:**

```bash
git clone https://github.com/yourusername/skillmapper.git
cd skillmapper
````

2. **Create a virtual environment and install dependencies:**

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install --no-cache-dir -r requirements.txt
```

3. **Create `.env` file with your credentials:**

```
REDIRECT_URI=http://127.0.0.1:8080/callback
CLIENT_ID=your_hh_client_id
CLIENT_SECRET=your_hh_client_secret
```

4. **Run the app:**

```bash
python3 main.py
```

5. **Authorize the application:**

* The app will open a browser window for hh.ru login and authorization.
* After successful authorization, the app will exchange the authorization code for tokens and fetch your resume recommendations.

---

## Usage

* The app fetches your resumes and displays recommended vacancies for the first resume found.
* Modify the code if you want to handle multiple resumes or customize the behavior.

---

## Notes

* This app uses Flask’s development server — **do not use in production**.
* Refresh token handling is implemented for access token renewal.
* Add your `.env` file to `.gitignore` to avoid committing sensitive credentials.

---

## License

MIT License

---

## Contact

For questions or issues, please open an issue or contact extroper@yandex.ru.
