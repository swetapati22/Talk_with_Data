import matplotlib
matplotlib.use('Agg')

from flask import Flask, request, jsonify, render_template_string
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import io
import os
import base64
import google.generativeai as genai

load_dotenv()

# Setup Flask
app = Flask(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)  # Replace with your real key
model = genai.GenerativeModel("gemini-2.0-flash")

# Upload form
UPLOAD_FORM = '''
<!doctype html>
<title>Upload CSV</title>
<h1>Upload a CSV File for Analysis</h1>
<form method=post enctype=multipart/form-data action="/upload">
  <input type=file name=file>
  <input type=submit value=Upload>
</form>
'''

@app.route('/')
def home():
    return render_template_string(UPLOAD_FORM)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if not file:
        return "No file uploaded", 400

    # Load CSV into pandas DataFrame
    df = pd.read_csv(file)

    # Generate sample preview
    sample = df.head(50).to_string(index=False)
    columns = df.columns.tolist()

    # Create prompt for Gemini
    prompt = f"""
    I have a CSV dataset with the following columns: {columns}

    Here are the first 50 rows:
    {sample}

    Please generate Python code that uses matplotlib or seaborn to create one meaningful visualization based on the dataset. 
    Assume the dataset is already loaded in a DataFrame called 'df'.
    Do not include markdown formatting or explanations. Just return clean Python code.
    """

    try:
        # Request response from Gemini model
        response = model.generate_content(prompt)
        code_string = response.text.strip("```python").strip("```")

        # Execute the code safely
        local_vars = {'df': df, 'plt': plt}
        exec(code_string, {}, local_vars)

        # Save the generated plot
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.clf()
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')

        # Return image and generated code
        img_html = f'<img src="data:image/png;base64,{image_base64}" style="max-width:100%;"/><br>'
        code_html = f"<h2>Generated Code:</h2><pre>{code_string}</pre>"
        return img_html + code_html

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
