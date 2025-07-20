# Agentic Data Analysis

This is an AI agent built in LangGraph that can perform data analysis on a provided dataset. It is to accompany my Youtube video to showcase some advanced LangGraph techniques.

Take a look at the below video for a demo:



https://github.com/user-attachments/assets/83bdc543-85ca-49c0-83a5-39d948f74286



## Getting Setup

### 1. Environment Configuration

First, create a `.env` file in the root directory with your configuration:

```bash
cp env.example .env
```

Then edit the `.env` file and add your OpenAI API key:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Dataset Setup

If you want to use the same dataset as me, you can download it from Kaggle below:

https://www.kaggle.com/datasets/computingvictor/transactions-fraud-datasets/data 

Otherwise feel free to upload your own dataset!

### 3. Installation

Install the requirements by running the following command:

```bash
pip install -r requirements.txt
```

### 4. Running the Application

Run the streamlit dashboard with the following command:

```bash
streamlit run data_analysis_streamlit_app.py
```

The application will automatically use the configuration from your `.env` file.

Enjoy!
