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
    body {{ font-family: Arial; padding: 40px; background: #f9f9f9; color: #333; }}
    h1 {{ color: #2c3e50; }}
    h3 {{ color: #34495e; }}
    img {{ border: 1px solid #ccc; margin-bottom: 10px; max-width: 100%; }}
    pre {{ background: #f4f4f4; padding: 10px; border-left: 4px solid #3498db; overflow-x: auto; }}
    .viz-block {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 40px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }}
    .error {{ color: red; font-style: italic; }}
    .upload-form {{ margin-bottom: 30px; }}
  </style>
</head>
<body>
  <h1>📊 Gemini AI Visualizations</h1>
  <form method="post" enctype="multipart/form-data" action="/upload" class="upload-form">
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

@app.route('/upload', methods=['POST'])
@app.route('/analyze', methods=['POST'])
def upload():
    file = request.files.get('file')
    if not file:
        return render_template_string(UPLOAD_FORM.format(output="<p class='error'>No file uploaded.</p>"))

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
   - Provide a short 2-line summary starting with 'Summary:'
   - Then return ONLY the valid raw Python code (no markdown formatting, no ``` backticks).
5. Assume the DataFrame is already loaded as 'df'.

Respond with plain text.
"""

    try:
        response = model.generate_content(prompt)
        full_response = response.text.strip()

        blocks = full_response.split("Summary:")
        visualizations = []

        for block in blocks[1:]:
            summary_line, *code_lines = block.strip().split("\n")
            summary = summary_line.strip()
            code = "\n".join([line for line in code_lines if line.strip()])

            try:
                plt.clf()
                local_vars = {'df': df, 'plt': plt, 'sns': sns}

                # Attempt execution
                try:
                    exec(code, {}, local_vars)
                except Exception as exec_error:
                    # Try fallback for heatmap
                    if 'heatmap' in code and 'df.corr()' in code:
                        fixed_code = code.replace("df.corr()", "df.select_dtypes(include='number').corr()")
                        exec(fixed_code, {}, local_vars)
                        code = fixed_code  # Update to show the fallback code
                    else:
                        raise exec_error

                # Capture plot
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

        # Build HTML output
        html_output = ""
        for i, viz in enumerate(visualizations, start=1):
            html_output += f"<div class='viz-block'>"
            html_output += f"<h3>Visualization {i}</h3>"
            html_output += f"<p>{viz['summary']}</p>"
            if viz['image']:
                html_output += f"<img src='data:image/png;base64,{viz['image']}'><br>"
            else:
                html_output += f"<p class='error'>⚠️ Could not render plot: {viz['error']}</p>"
            html_output += f"<pre>{viz['code']}</pre>"
            html_output += "</div>"

        return render_template_string(UPLOAD_FORM.format(output=html_output))

    except Exception as e:
        return render_template_string(UPLOAD_FORM.format(output=f"<p class='error'>Unexpected error: {e}</p>"))

if __name__ == '__main__':
    app.run(debug=True)
