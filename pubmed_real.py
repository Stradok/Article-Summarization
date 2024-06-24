# -*- coding: utf-8 -*-
"""PUBMED-Real.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/13oqxZIYi0quapqHN1DBu1d1wQ9zB6E4P
"""

!pip install datasets

from datasets import load_dataset

ds = load_dataset("ccdv/pubmed-summarization", "document")
train = ds['train']
test = ds['test']
validation = ds['validation']

import pandas as pd
import numpy as np
import nltk
nltk.download('punkt')
nltk.download('stopwords')

train_df = pd.DataFrame(train)
test_df = pd.DataFrame(test)
validation_df = pd.DataFrame(validation)

train_df

"""**Preprocessing**"""

import pandas as pd
from datasets import load_dataset
from transformers import AutoTokenizer



tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")

# Tokenization function
def tokenize_function(examples):
    return tokenizer(examples['article'], padding="max_length", truncation=True, max_length=1024)

# Tokenize the datasets
train_dataset = ds['train'].map(tokenize_function, batched=True)
test_dataset = ds['test'].map(tokenize_function, batched=True)
validation_dataset = ds['validation'].map(tokenize_function, batched=True)

import re

# Function to preprocess text
def preprocess_text(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
    text = re.sub(r'\[.*?\]', '', text)  # Remove text inside square brackets
    text = re.sub(r'\(.*?\)', '', text)  # Remove text inside parentheses
    text = re.sub(r'\W', ' ', text)  # Remove special characters
    text = re.sub(r'\d', '', text)  # Remove digits
    return text.strip()

# Apply preprocessing to both articles and abstracts
train_df['article'] = train_df['article'].apply(preprocess_text)
train_df['abstract'] = train_df['abstract'].apply(preprocess_text)

# Install required dependencies
!pip install transformers[torch]
!pip install accelerate -U

import pandas as pd
import re
from datasets import Dataset
from transformers import AutoTokenizer, BartForConditionalGeneration, DataCollatorForSeq2Seq, Trainer, TrainingArguments

# Load the tokenizer
tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")

# Tokenization function
def tokenize_function(examples):
    # Tokenize the article and the abstract
    model_inputs = tokenizer(examples['article'], max_length=1024, padding="max_length", truncation=True)
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(examples['abstract'], max_length=150, padding="max_length", truncation=True)
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

# Convert DataFrames to Dataset format required by transformers
train_dataset = Dataset.from_pandas(train_df)
val_dataset = Dataset.from_pandas(val_df)
test_dataset = Dataset.from_pandas(test_df)

# Tokenize the datasets
tokenized_train_dataset = train_dataset.map(tokenize_function, batched=True)
tokenized_val_dataset = val_dataset.map(tokenize_function, batched=True)
tokenized_test_dataset = test_dataset.map(tokenize_function, batched=True)

# Data collator for padding
data_collator = DataCollatorForSeq2Seq(tokenizer, model=None)

# Load the model
model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")

# Training arguments
training_args = TrainingArguments(
    output_dir='./results',
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    weight_decay=0.01,
    save_total_limit=3,
    num_train_epochs=3,
    predict_with_generate=True
)

# Initialize Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train_dataset,
    eval_dataset=tokenized_val_dataset,
    data_collator=data_collator,
    tokenizer=tokenizer
)

# Start training
trainer.train()

"""**BART**"""

from transformers import BartForConditionalGeneration

# Load the model
bart_model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")

# Summarization function
def summarize_bart(text):
    inputs = tokenizer(text, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = bart_model.generate(inputs["input_ids"], num_beams=4, max_length=150, early_stopping=True)
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

# Example usage
example_text = test_df.iloc[55]['article']
print("Original text:\n", example_text)
print("\nBART Summary:\n", summarize_bart(example_text))

"""**FLASK**"""

!pip install flask-ngrok
import os

# Create directories
os.makedirs('templates', exist_ok=True)
os.makedirs('static', exist_ok=True)

from google.colab import files

# Upload 'BG.jpg' from your local machine
uploaded = files.upload()

# Move the uploaded file to the correct directory
import shutil
shutil.move(next(iter(uploaded)), 'static/BG.jpg')

# Create your HTML file
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Text Summarization</title>
<style>
    /* General styles */
    body {
        font-family: Arial, sans-serif;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        background-image: url('BG.jpg');
        background-size: cover;
        background-position: center;
        margin: 0;
    }

    .container {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 80%;
        max-width: 800px;
        background-color: rgba(255, 255, 255, 0.9); /* White with transparency */
        padding: 20px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        border-radius: 8px;
    }

    .boxes {
        display: flex;
        justify-content: space-between;
        width: 100%;
        margin-bottom: 20px;
    }

    .box {
        flex: 1;
        padding: 20px;
        margin: 10px;
        background-color: rgba(0, 0, 0, 0.05);
        border-radius: 8px;
    }

    /* Input and output text areas */
    .box textarea {
        width: 100%;
        height: 100%;
        padding: 10px;
        margin-top: 10px;
        border: none;
        border-radius: 6px;
        background-color: rgba(255, 255, 255, 0.8);
        transition: background-color 0.3s ease;
    }

    .box textarea:focus {
        background-color: rgba(255, 255, 255, 1);
    }

    .box textarea::placeholder {
        color: rgba(0, 0, 0, 0.5);
    }

    /* Summarize button */
    .button {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
    }

    .button button {
        padding: 12px 24px;
        border: none;
        border-radius: 6px;
        background-color: #007bff;
        color: #fff;
        font-size: 16px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }

    .button button:hover {
        background-color: #0056b3;
    }
</style>
</head>
<body>
    <div class="container">
        <div class="boxes">
            <!-- Left box for input -->
            <div class="box">
                <textarea id="inputText" placeholder="Enter text to summarize..." rows="10"></textarea>
            </div>

            <!-- Right box for output -->
            <div class="box">
                <textarea id="outputText" placeholder="Summarized text will appear here..." rows="10" readonly></textarea>
            </div>
        </div>

        <!-- Button for summarization -->
        <div class="button">
            <button onclick="summarize()">Summarize</button>
        </div>
    </div>

    <!-- Script for summarization logic -->
    <script>
        function summarize() {
            // Fetch input text
            var inputText = document.getElementById("inputText").value;

            // Example summarization logic (replace with your actual logic)
            // This is a placeholder function and does not perform actual summarization
            var summarizedText = "This is a summarized text output.";

            // Update output textarea with summarized text
            document.getElementById("outputText").value = summarizedText;
        }
    </script>
</body>
</html>

"""

with open("templates/index.html", "w") as file:
    file.write(html_content)

from flask_ngrok import run_with_ngrok
from flask import Flask, render_template, request, jsonify
from transformers import BartForConditionalGeneration, BartTokenizer

app = Flask(__name__)
run_with_ngrok(app)

# Load the BART model and tokenizer
bart_model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")
tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")

# Summarization function using BART
def summarize_bart(text):
    inputs = tokenizer(text, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = bart_model.generate(inputs["input_ids"], num_beams=4, max_length=150, early_stopping=True)
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

# Route to serve index.html (if using templates)
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle summarize request
@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    input_text = data['input_text']
    summary = summarize_bart(input_text)
    return jsonify({'summary': summary})

if __name__ == '__main__':
    app.run()

"""**Now Using Chat GPT API**"""

OPENAI_API_KEY = 'Your Own API key'

from transformers import BartForConditionalGeneration, BartTokenizer
import requests
bart_model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")
tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
def summarize_bart(text):
    inputs = tokenizer(text, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = bart_model.generate(inputs["input_ids"], num_beams=4, max_length=150, early_stopping=True)


def summarize_gpt3(text):
    endpoint = "https://api.openai.com/v1/engines/davinci/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    data = {
        "prompt": text,
        "max_tokens": 150,
        "temperature": 0.7,
        "top_p": 1.0,
        "stop": "\n"
    }
    response = requests.post(endpoint, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["text"].strip()
    else:
        return f"Error: {response.status_code}, {response.text}"

example_text = test_df.iloc[0]['article']
print("Original text:\n", example_text)
print("\nGPT-3 Summary:\n", summarize_gpt3(example_text))