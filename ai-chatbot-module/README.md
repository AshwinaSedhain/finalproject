# AI Chatbot Module — Universal Domain-Aware Natural Language → SQL (v2.0.0)

**Status:** Production Ready
**License:** MIT
**Last Updated:** October 2024

---
# create a .env file

Get Groq API Key (FREE)

Visit https://console.groq.com in your browser

1.Sign up or log in to your account

2.Navigate to the "API Keys" section

3.Click "Create API Key"

4.Give your key a name (e.g., "datachatbot")

5.Click "Create" or "Generate"

6.Copy the generated API key (it starts with "gsk_")

7.Paste the key into your .env file:

GROQ_API_KEY=your_copied_key_here(write this onlt line api key here)

Save the .env file



## Overview

A production-ready Python module that converts natural language questions into SQL queries, auto-detects the database domain, and returns domain-aware business insights with visualizations. Designed to integrate easily with frontend apps (Streamlit, React, Vue) or backend services.

## What it does

* Translates plain English into executable SQL.
* Detects database domain (Healthcare, Finance, Retail, Education, HR, Logistics, etc.) automatically.
* Generates natural-language insights and appropriate visualizations.
* Optionally executes generated SQL via a provided `execute_query` callback.
* Adapts phrasing and chart style to the detected domain.

## Core features

* **Auto-domain detection** with confidence scoring
* **Intent classification** (query_data, analyze_metrics, compare, trend, filter, top_bottom, generate_report)
* **SQL generation** using an LLM backend (Groq API in this release)
* **Query validation & sanitization** (safety layer before execution)
* **Auto-visualizer** (Plotly-based interactive figures)
* **Plug-and-play execution** via a user-supplied `execute_query(sql)` function
* **Frontend-ready payloads** (serializable visualizations + SQL)

## Architecture & Components

The module is organized into five main components:

1. **Intent Classifier**

   * Model: Sentence Transformers `all-MiniLM-L6-v2`
   * Responsibilities: Detect intent and extract entities (metrics, dimensions, time ranges).

2. **Domain Detector**

   * Inputs: Database schema (tables and columns)
   * Method: Keyword matching + semantic similarity, returns confidence per domain.

3. **Query Generator**

   * LLM calls to Groq (Llama 3.3 70B in this release)
   * Produces a candidate SQL query and explanatory comments
   * Includes domain-specific SQL hints and constraints

4. **Response Generator**

   * Uses LLM to create a human-readable summary of results and business insights
   * Formats output based on domain tone and vocabulary

5. **Auto Visualizer**

   * Library: Plotly
   * Chooses chart type and prepares interactive HTML/JSON serializable figures

### Data flow

1. User asks a question → 2. Intent classified → 3. Domain detected from schema → 4. SQL generated → 5. (Optional) SQL executed by provided callback → 6. Response + visualization generated → 7. Result returned

## Technology stack & dependencies

* **Python**: 3.8+
* **LLM**: Groq API (Llama 3.3 70B) — configurable via `GROQ_API_KEY`
* **Embeddings / NLU**: `sentence-transformers` (all-MiniLM-L6-v2)
* **DL runtime**: PyTorch
* **Data**: pandas, numpy
* **Visualization**: plotly, kaleido (export)
* **Env**: python-dotenv

**Pinned dependencies (tested):**

```
groq==0.4.1
sentence-transformers==2.3.1
torch>=2.2.0
pandas==2.1.4
numpy==1.26.3
plotly==5.18.0
kaleido==0.2.1
python-dotenv==1.0.0
```

*Total install size approx: 1.1 GB*

## Installation

### Prerequisites

* Python 3.8+ and `pip` available
* Internet connection to call Groq API
* Minimum 2GB free disk (8GB RAM recommended)

### Steps

1. Clone repository and change directory

```bash
git clone <repo-url>
cd ai-chatbot-module
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Create `.env` from example and add API key

```bash
cp .env.example .env
# edit .env and set GROQ_API_KEY
```

4. Run quick test

```bash
python quick_test.py
```

If everything initializes, the quick test prints success for Intent Classifier, Query Generator, Response Generator, and Visualizer.

## Quick start

Example usage:

```python
from chatbot import ChatbotAgent

chatbot = ChatbotAgent()

database_schema = {
  "sales": ["id", "date", "product", "amount", "region"],
  "customers": ["id", "name", "email", "total_purchases"]n}

result = chatbot.process(
  user_prompt="Show me total sales by product",
  database_schema=database_schema
)

print(result['response'])
print(result['generated_query'])
```

### With database execution

```python
from sqlalchemy import create_engine
import pandas as pd

def execute_query(sql: str):
    return pd.read_sql(sql, engine)

engine = create_engine('postgresql://user:pass@localhost/db')

result = chatbot.process(
  user_prompt="Top 10 customers by purchases",
  database_schema=schema,
  execute_query=execute_query
)
```

## API / Public interface

### `ChatbotAgent` class

**Initialization**

```python
chatbot = ChatbotAgent()
```

**Main method: `process()`**

```python
result = chatbot.process(
    user_prompt: str,
    database_schema: dict,
    execute_query: callable = None
)
```

**Returns** a dictionary with keys: `success`, `domain`, `domain_confidence`, `all_domain_scores`, `intent`, `generated_query`, `query_results`, `response`, `visualization`, `chart_type`, `error`

### Helper utilities

* `get_supported_domains()` — lists domains and keyword triggers
* `analyze_schema(database_schema)` — analyze schema and return domain confidence

## Integration guides

**Streamlit** — example provided in `docs/streamlit_example.py` (caching patterns included)
**React** — example component `ChatInterface.jsx` (axios POST to your server API)
**Vue** — example component `ChatInterface.vue`

> See `/examples` folder for ready-to-run templates.

## Performance & limits

* Typical response time (LLM + pipeline): 3–5 seconds (depends on Groq latency and network)
* Caching available for repeated queries
* Concurrency supported (thread/process safe depending on LLM client)

## Security & best practices

* **Never** commit `.env` or API keys to source control
* Validate / sanitize generated SQL before execution (the module performs basic cleaning but treat as advisory)
* Use least-privilege DB accounts for query execution
* Enable request quotas and rate limits on the LLM API key

## Troubleshooting

* **LLM errors**: Ensure `GROQ_API_KEY` present and valid
* **Missing schema**: Provide complete mapping `{table: [cols]}`
* **Plotting issues**: Ensure `kaleido` installed for static exports

## Changelog

* **v2.0.0** — Production-ready; auto-domain detection, improved SQL sanitization, Plotly visualizer

## License

MIT — see `LICENSE` file.

---

# Integration Guide for Frontend Team

Streamlit Integration

Complete implementation for Streamlit-based user interface:


import streamlit as st
from chatbot import ChatbotAgent
import pandas as pd
from sqlalchemy import create_engine

st.set_page_config(page_title="AI Data Assistant", layout="wide")

@st.cache_resource
def initialize_chatbot():
    return ChatbotAgent()

chatbot = initialize_chatbot()

@st.cache_resource
def get_db_connection():
    return create_engine('postgresql://user:pass@localhost/db')

engine = get_db_connection()

@st.cache_data
def get_schema():
    from sqlalchemy import inspect
    inspector = inspect(engine)
    schema = {}
    for table_name in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        schema[table_name] = columns
    return schema

database_schema = get_schema()

def execute_query(sql):
    return pd.read_sql(sql, engine)

st.title("AI Data Assistant")

with st.sidebar:
    st.header("Settings")
    show_sql = st.checkbox("Show SQL Query", value=True)
    show_raw_data = st.checkbox("Show Raw Data", value=False)

question = st.text_input("Your Question:", placeholder="e.g., Show me top 10 products by sales")

if st.button("Ask", type="primary"):
    if question:
        with st.spinner("Processing..."):
            result = chatbot.process(
                user_prompt=question,
                database_schema=database_schema,
                execute_query=execute_query
            )
        
        if result['success']:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Detected Domain", result['domain'].title())
            with col2:
                st.metric("Confidence", f"{result['domain_confidence']:.0%}")
            
            st.subheader("Answer")
            st.write(result['response'])
            
            if result['visualization']:
                st.plotly_chart(result['visualization'], use_container_width=True)
            
            if show_sql:
                with st.expander("View SQL"):
                    st.code(result['generated_query'], language='sql')
            
            if show_raw_data and result['query_results'] is not None:
                with st.expander("View Data"):
                    st.dataframe(result['query_results'])
        else:
            st.error(f"Error: {result.get('error')}")


#  React Integration

JavaScript

import React, { useState } from 'react';
import axios from 'axios';
import Plot from 'react-plotly.js';

function ChatInterface() {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('/api/query', {
        question: question
      });

      if (response.data.success) {
        setResult(response.data);
      } else {
        setError(response.data.error);
      }
    } catch (err) {
      setError('Failed to process question');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-interface">
      <h1>AI Data Assistant</h1>

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question..."
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Processing...' : 'Ask'}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      {result && (
        <div className="results">
          <div className="domain-info">
            Domain: {result.domain} ({(result.domain_confidence * 100).toFixed(0)}%)
          </div>
          
          <div className="response">
            <h3>Answer:</h3>
            <p>{result.response}</p>
          </div>

          {result.visualization && (
            <div className="chart">
              <Plot data={JSON.parse(result.visualization).data} 
                    layout={JSON.parse(result.visualization).layout} />
            </div>
          )}

          <details>
            <summary>View SQL</summary>
            <pre><code>{result.generated_query}</code></pre>
          </details>
        </div>
      )}
    </div>
  );
}

export default ChatInterface;

# What  Chatbot Provides 

# For Frontend Team


result = chatbot.process(question, schema, execute_query)

# They get:
{
    "success": True,
    "domain": "healthcare",              # Auto-detected
    "domain_confidence": 0.89,           # Confidence score
    "generated_query": "SELECT ...",     # SQL query
    "query_results": DataFrame,          # Data
    "response": "Business insights...",  # Natural language
    "visualization": plotly_figure,      # Chart object
    "chart_type": "bar"                  # Chart type
}
What they need to do:

Display the response text
Show the chart (Plotly component)
Optional: Show SQL query
Optional: Show raw data table


# For Backend Team

Complete chatbot module (import and use)
Clear API documentation
Integration examples (Flask, FastAPI, Django)
What they need to do:

Create API endpoint that calls your chatbot
Convert DataFrame to JSON
Convert Plotly figure to JSON
Add authentication (their responsibility)
Add activity logging (their responsibility)


# Integration Checklist for Team
Step 1: Database Team (1-2 hours)
 Extract database schema
 Create execute_query function
 Test database connection
 Share with backend team
Step 2: Backend Team (2-4 hours)
 Import your chatbot module
 Create API endpoint
 Integrate database functions
 Test API
 Add authentication
 Deploy API
Step 3: Frontend Team (1-2 hours)
 Call backend API
 Display response text
 Display chart
 Add user input form
 Test integration
Step 4: Testing (1 day)
 Test with real database
 Test different question types
 Test all domains
 Performance testing
 User acceptance testing


# How Different Teams Use quick_test.py
Frontend Team:

# Before integrating:
python quick_test.py

# Checks:
- Does chatbot work?
- What does output look like?
- How to use the API?




# Backend Team:

# After installing module:
python quick_test.py

# Verifies:
- Installation successful
- API key configured
- Module imports correctly


#  Database Team:

# Before providing schema:
python quick_test.py

# Understands:
- What schema format needed
- How execute_query works
- Expected output format



#  QA Team:

# During testing:
python quick_test.py

# Validates:
- Core functionality works
- No regressions
- Performance baseline