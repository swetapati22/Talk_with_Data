import matplotlib
matplotlib.use('Agg')

from flask import Flask, request, jsonify, render_template_string
import pandas as pd
from dotenv import load_dotenv
import os
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Setup Flask
app = Flask(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# HTML Upload Form
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

    df = pd.read_csv(file)
    sample = df.head(50).to_string(index=False)
    columns = df.columns.tolist()

    # Updated prompt to ask for multiple visualizations
    prompt = f"""
I have a CSV dataset with the following columns: {columns}

Here are the first 50 rows:
{sample}

Please generate 5 different Python code snippets using matplotlib or seaborn, each showing a different and meaningful visualization based on this dataset. 
Assume the dataset is already loaded in a DataFrame called 'df'.
Do not include markdown formatting or explanations — only the raw Python code for each plot. Separate each code snippet clearly.
"""

    try:
        response = model.generate_content(prompt)
        raw_response = response.text

        # Split response into individual code blocks
        code_blocks = [blk for blk in raw_response.strip().split("```python") if blk.strip()]
        visualizations = []
        
        for code in code_blocks:
            # Extract code portion
            if "```" in code:
                code = code.split("```")[0]
            code = code.strip()
            if not code:
                continue

            # Clear previous plot
            plt.clf()

            # Provide both plt and sns in exec context
            local_vars = {'df': df, 'plt': plt, 'sns': sns}
            try:
                exec(code, {}, local_vars)

                # Save plot to image buffer
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                image_base64 = base64.b64encode(buf.read()).decode('utf-8')

                visualizations.append({'image': image_base64, 'code': code})

            except Exception as plot_error:
                visualizations.append({'image': '', 'code': f"# Failed to execute code:\n{code}\n# Error: {plot_error}"})

        # Render all plots and code in HTML
        html_output = ''
        for i, viz in enumerate(visualizations, start=1):
            if viz['image']:
                html_output += f"<h3>Visualization {i}</h3>"
                html_output += f"<img src='data:image/png;base64,{viz['image']}' style='max-width:100%;'/><br>"
            else:
                html_output += f"<h3>Visualization {i} - Error generating image</h3>"
            html_output += f"<pre>{viz['code']}</pre>"

        return html_output

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
