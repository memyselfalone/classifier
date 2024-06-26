import os
from flask import Flask, request, render_template, send_file, redirect, url_for
import PyPDF2
import nltk
from nltk.tokenize import sent_tokenize
import pandas as pd

nltk.download('punkt')

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

def read_pdf(file_path):
    pdf_file = open(file_path, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_file)
    text = ''
    for page in range(pdf_reader.numPages):
        text += pdf_reader.getPage(page).extract_text()
    pdf_file.close()
    return text

def read_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

def process_text(text):
    sentences = sent_tokenize(text)
    pairs = []
    for i in range(len(sentences) - 1):
        question = sentences[i]
        answer = sentences[i + 1]
        pairs.append((question, answer))
    return pairs

def save_to_csv(pairs, output_file):
    df = pd.DataFrame(pairs, columns=['Question', 'Answer'])
    df.to_csv(output_file, index=False)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and (file.filename.endswith('.pdf') or file.filename.endswith('.txt')):
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)

            if file.filename.endswith('.pdf'):
                text = read_pdf(file_path)
            elif file.filename.endswith('.txt'):
                text = read_txt(file_path)
            else:
                return "Unsupported file format", 400

            pairs = process_text(text)
            output_file = os.path.join(OUTPUT_FOLDER, file.filename.split('.')[0] + '.csv')
            save_to_csv(pairs, output_file)

            return redirect(url_for('download_file', filename=os.path.basename(output_file)))

    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(OUTPUT_FOLDER, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
