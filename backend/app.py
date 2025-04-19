from flask import Flask, request, jsonify
import pandas as pd
from dotenv import load_dotenv
import os
import matplotlib.pyplot as plt
import io
import base64
import google.generativeai as genai

# Setup Flask
app = Flask(__name__)

# Configure Gemini API
genai.configure(api_key="GEMINI_API_KEY")
model = genai.GenerativeModel("gemini-pro")

@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files['file']
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

        return jsonify({'image': image_base64, 'code': code_string})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
