# MacroSnap

MacroSnap is a Streamlit app that uses Gemini to estimate meal calories and macros from a text description or photo.

## Features

- Name and WhatsApp number onboarding
- Gemini chat for meal estimates
- Meal photo analysis
- A WhatsApp-friendly nutrition summary preview

**WhatsApp delivery is not enabled in this version.** The summary is shown as a preview. Twilio trial accounts require an approved message template, and the app is not currently connected to one.

## Run locally

1. Install Python.
2. Open a terminal in the project folder and create a virtual environment:

   ```powershell
   python -m venv venv
   ```

3. Activate it in PowerShell:

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

4. Install the packages:

   ```powershell
   pip install -r requirements.txt
   ```

5. Create `.streamlit/secrets.toml` with your Gemini API key:

   ```toml
   GEMINI_API_KEY = "paste-your-own-key-here"
   ```

6. Start the app:

   ```powershell
   streamlit run app.py
   ```

Keep `secrets.toml` private. Do not upload API keys or the `venv` folder to GitHub. The repository's `.gitignore` excludes them.

## Current project status

The local app has been opened and the text chat, photo analysis, and summary preview have been tried. Nutrition values are estimates and may vary with portions and ingredients.
