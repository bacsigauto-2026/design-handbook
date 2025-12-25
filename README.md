# Design Handbook Dashboard

A Streamlit application for managing and viewing design drawings, featuring role-based access control and PDF integration.

## 🚀 Features

- **Dashboard**: View and filter design documents.
- **PDF Viewer**: Embedded PDF viewer with full-screen support.
- **Role-Based Access**:
    - **User**: View access only.
    - **Admin**: Manage user roles and permissions.
- **Authentication**: Google OAuth via Supabase (or email simulation).

## 🛠️ Local Installation

1.  **Clone the repository**
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Setup Secrets**:
    Create a file `.streamlit/secrets.toml`:
    ```toml
    [supabase]
    url = "YOUR_SUPABASE_URL"
    key = "YOUR_SUPABASE_ANON_KEY"
    ```
4.  **Run the App**:
    ```bash
    streamlit run app.py
    ```

## ☁️ Deployment Guide (Streamlit Community Cloud)

This app is ready to easily deploy on Streamlit Community Cloud.

### 1. Push to GitHub
Ensure your code is pushed to a GitHub repository.

### 2. Deploy on Streamlit
1.  Go to [share.streamlit.io](https://share.streamlit.io/).
2.  Click **"New app"**.
3.  Select your repository, branch, and main file (`app.py`).
4.  Click **"Deploy!"**.

### 3. Configure Secrets (CRITICAL)
Once the app is deploying (or if it fails initially due to missing secrets):
1.  In your app dashboard, click **"Manage app"** (bottom right) or the **Settings** menu.
2.  Go to **"Secrets"**.
3.  Paste the contents of your local `.streamlit/secrets.toml` into the secrets area:
    ```toml
    [supabase]
    url = "YOUR_SUPABASE_URL"
    key = "YOUR_SUPABASE_ANON_KEY"
    ```
4.  Click **"Save"**. The app should restart and connect successfully.

## ℹ️ Troubleshooting
- **"Secrets not found"**: Ensure you pasted the TOML content correctly in the Streamlit Cloud settings.
- **Database Error**: Verify your Supabase project is active and the `users` and `design_docs` tables exist.
