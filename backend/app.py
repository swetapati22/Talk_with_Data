import matplotlib
matplotlib.use('Agg')

from flask import Flask, request, jsonify
import pandas as pd
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import seaborn as sns
import io
import os
import base64
import google.generativeai as genai
from flask_cors import CORS

load_dotenv()

# Setup Flask
app = Flask(__name__)
CORS(app)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

@app.route('/analyze', methods=['POST'])
def upload():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400

    df = pd.read_csv(file)
    sample = df.head(50).to_string(index=False)
    columns = df.columns.tolist()

    # Prompt for Gemini
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
            if "```" in code:
                code = code.split("```")[0]
            code = code.strip()
            if not code:
                continue

            # Clear previous plots
            plt.clf()

            # Provide plt and sns in context
            local_vars = {'df': df, 'plt': plt, 'sns': sns}
            try:
                exec(code, {}, local_vars)

                # Save plot
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                image_base64 = base64.b64encode(buf.read()).decode('utf-8')

                visualizations.append({'image': image_base64, 'code': code})

            except Exception as plot_error:
                visualizations.append({'image': '', 'code': f"# Error generating this plot:\n{code}\n\n# Error: {plot_error}"})

        return jsonify({'visualizations': visualizations})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
