# MacroSnap

MacroSnap is a Streamlit app that uses Google Gemini to estimate calories and macronutrients from a meal description or photo.

## Features

- Enter your name and WhatsApp number
- Describe a meal and get a nutrition estimate
- Upload a meal photo for analysis
- View a WhatsApp-style nutrition summary

## Requirements

- Python 3.10 or later
- A Google Gemini API key

## Run locally

1. Clone or download this repository and open a terminal in its folder.
2. Create and activate a virtual environment in PowerShell:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install the dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Create `.streamlit/secrets.toml` and add your Gemini API key:

   ```toml
   GEMINI_API_KEY = "your-gemini-api-key"
   ```

5. Start the app:

   ```powershell
   streamlit run app.py
   ```

## Deploy on Streamlit Community Cloud

1. Connect your GitHub account to Streamlit Community Cloud.
2. Select this repository, the `main` branch, and `app.py`.
3. Add `GEMINI_API_KEY` in the app’s **Secrets** settings.
4. Deploy the app.

## WhatsApp

This version does not send WhatsApp messages. It displays a WhatsApp-style summary preview.

## Note

Nutrition values are estimates. Actual values depend on portion sizes and ingredients.
