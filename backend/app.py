import matplotlib
matplotlib.use('Agg')

from flask import Flask, request, jsonify, render_template_string
import pandas as pd
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import seaborn as sns
import io
import os
import base64
import google.generativeai as genai
from flask_cors import CORS
import re

# Load .env variables
load_dotenv()

# Setup Flask
app = Flask(__name__)
CORS(app)

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")

# Upload form HTML
UPLOAD_FORM = '''
<!doctype html>
<html>
<head>
  <title>Gemini AI Visualizations</title>
  <style>
    body {{
      font-family: 'Segoe UI', sans-serif;
      padding: 40px;
      background: linear-gradient(to bottom right, #ffecd2, #fcb69f);
      color: #333;
    }}
    h1 {{ color: #2c3e50; text-align: center; }}
    h3 {{ color: #34495e; }}
    img {{ border: 1px solid #ccc; margin-bottom: 10px; max-width: 100%; }}
    pre {{
      background: #f4f4f4;
      padding: 10px;
      border-left: 4px solid #3498db;
      overflow-x: auto;
      border-radius: 5px;
    }}
    .viz-block {{
      background: white;
      padding: 25px;
      border-radius: 12px;
      margin: 40px auto;
      box-shadow: 0 2px 15px rgba(0, 0, 0, 0.05);
      max-width: 900px;
    }}
    .error {{ color: red; font-style: italic; }}
    .upload-form {{
      margin-bottom: 30px;
      display: flex;
      justify-content: center;
      gap: 10px;
    }}
    .upload-form input[type="submit"] {{
      background-color: #3498db;
      color: white;
      border: none;
      padding: 10px 20px;
      border-radius: 5px;
      cursor: pointer;
    }}
    .upload-form input[type="file"] {{
      padding: 6px;
    }}
  </style>
</head>
<body>
  <h1>📊 CSV Visualization Generator</h1>
  <form method="post" enctype="multipart/form-data" action="/analyze" class="upload-form">
    <input type="file" name="file" required>
    <input type="submit" value="Upload CSV & Generate Plots">
  </form>
  {output}
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(UPLOAD_FORM.format(output=""))

@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files.get('file')
    if not file:
        error_msg = "<p class='error'>No file uploaded.</p>"
        if request.accept_mimetypes['application/json'] > request.accept_mimetypes['text/html']:
            return jsonify({'error': 'No file uploaded'}), 400
        else:
            return render_template_string(UPLOAD_FORM.format(output=error_msg))

    df = pd.read_csv(file)
    sample = df.head(50).to_string(index=False)
    columns = df.columns.tolist()

    prompt = f"""
You are a professional data analyst.

You're working with a CSV file with the following columns:
{columns}

Here are the first 50 rows:
{sample}

Please generate 5 meaningful Python visualizations using matplotlib or seaborn.

Rules:
1. The first plot MUST be a correlation heatmap of all numeric columns.
2. The remaining 4 plots should be diverse — such as barplots, lineplots, boxplots, scatter, histograms — depending on what makes sense from this data.
3. Use ONLY column names that appear in the dataset. DO NOT use placeholders like 'col1', 'col2', etc.
4. For each visualization:
   - Provide a short summary starting with 'Summary:' and include two concise, meaningful insights (separated by a period or semicolon).
   - Then return ONLY the valid raw Python code (no markdown formatting, no ``` backticks).
5. Assume the DataFrame is already loaded as 'df'.

Respond with plain text.
"""

    try:
        response = model.generate_content(prompt)
        full_response = response.text.strip()

        blocks = re.split(r"\n*Summary:\s*", full_response)
        visualizations = []

        for block in blocks[1:]:
            if not block.strip():
                continue

            lines = block.strip().splitlines()
            summary = lines[0].strip()

            code_start = 0
            for i, line in enumerate(lines[1:], start=1):
                if line.strip().startswith(('df.', 'plt.', 'sns.', 'fig', 'ax', 'import', 'for', 'if')):
                    code_start = i
                    break

            code_lines = lines[code_start:]
            code = "\n".join([line.strip("` ").replace("```", "") for line in code_lines if line.strip()])
            code = "\n".join(code_lines)

            try:
                plt.clf()
                local_vars = {'df': df, 'plt': plt, 'sns': sns}

                try:
                    exec(code, {}, local_vars)
                except Exception as exec_error:
                    if 'heatmap' in code and 'df.corr()' in code:
                        fixed_code = code.replace("df.corr()", "df.select_dtypes(include='number').corr()")
                        exec(fixed_code, {}, local_vars)
                        code = fixed_code
                    else:
                        raise exec_error

                buf = io.BytesIO()
                fig = plt.gcf()
                fig.tight_layout()
                fig.savefig(buf, format='png')
                buf.seek(0)
                image_base64 = base64.b64encode(buf.read()).decode('utf-8')
                plt.clf()

                visualizations.append({
                    'summary': summary,
                    'code': code,
                    'image': image_base64,
                    'error': None
                })

            except Exception as e:
                visualizations.append({
                    'summary': summary,
                    'code': code,
                    'image': None,
                    'error': str(e)
                })

        if request.accept_mimetypes['application/json'] > request.accept_mimetypes['text/html']:
            return jsonify({'visualizations': visualizations})

        html_output = ""
        for i, viz in enumerate(visualizations, start=1):
            html_output += f"<div class='viz-block'>"
            html_output += f"<h3>Visualization {i}</h3>"
            html_output += f"<p><strong>Summary:</strong> {viz['summary']}</p>"
            if viz['image']:
                html_output += f"<img src='data:image/png;base64,{viz['image']}'><br>"
            else:
                html_output += f"<p class='error'>⚠️ Could not render plot: {viz['error']}</p>"
            html_output += f"<pre>{viz['code']}</pre>"
            html_output += "</div>"

        return render_template_string(UPLOAD_FORM.format(output=html_output))

    except Exception as e:
        if request.accept_mimetypes['application/json'] > request.accept_mimetypes['text/html']:
            return jsonify({'error': f'Unexpected error: {str(e)}'}), 500
        else:
            return render_template_string(UPLOAD_FORM.format(
                output=f"<p class='error'>Unexpected error: {e}</p>"
            ))

@app.route('/routes')
def show_routes():
    return jsonify([str(rule) for rule in app.url_map.iter_rules()])

if __name__ == '__main__':
    app.run(debug=True)
