# -*- coding: utf-8 -*-
"""
Created on Fri Aug  2 15:30:40 2024

@author: ASUS
"""

import streamlit as st
import random
import time
import pandas as pd
import os
import uuid
from datetime import datetime
import string
from streamlit_feedback import streamlit_feedback
from st_copy_to_clipboard import st_copy_to_clipboard

# Set page configuration
st.set_page_config(page_title="BrokerBuddyFAKE2", page_icon="📖", layout="wide")

# Add custom CSS styles to adjust padding
st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                }
        </style>
        """, unsafe_allow_html=True)

# Initialize session state variables
if 'feedback_df' not in st.session_state:
    st.session_state.feedback_df = pd.DataFrame(columns=['Question', 'Answer', 'Score', 'Text'])

if 'feedback_given' not in st.session_state:
    st.session_state.feedback_given = False

if 'fbk' not in st.session_state:
    st.session_state.fbk = str(uuid.uuid4())

if 'last_question' not in st.session_state:
    st.session_state.last_question = ""

if 'last_answer' not in st.session_state:
    st.session_state.last_answer = ""

if 'search_results' not in st.session_state:
    st.session_state.search_results = []

# Directory to save feedback data
#directory = r"C:\Users\Cesar.Salgado\Documents\ticket2_thumbs\tempDir"
#os.makedirs(directory, exist_ok=True)  # Ensure the directory exists

# Function to generate a random response
def response_generator():
    return random.choice([
        "Muchos años después, frente al pelotón de fusilamiento, el coronel Aureliano Buendía",
        "Había de recordar aquella tarde remota en que su padre lo llevó a conocer el hielo",
        "Macondo era entonces una aldea de veinte casas hechas de barro y cañabrava construidas",
        "Construidas a orillas de un río de aguas diáfanas que se precipitaban por un lecho de piedras",
        "Pulidas, blancas y enormes como huevos prehistóricos. El mundo era tan reciente que muchas cosas"
    ])

# Generator function for typewriter effect
def typewriter_effect(text):
    message = ""
    for word in text.split():
        message += word + " "
        yield message
        time.sleep(0.05)

# Function to display the answer
def display_answer(answer):
    typewriter_placeholder = st.empty()
    for partial_text in typewriter_effect(answer):
        typewriter_placeholder.write(partial_text)

# Function to handle feedback submission
def fbcb(response):
    st.session_state.feedback_given = True  # Mark feedback as given

    # Map thumbs to 'good' and 'bad'
    score = response.get('score')
    mapped_score = "good" if score == "👍" else "bad" if score == "👎" else "unknown"

    # Append feedback to the DataFrame
    feedback_data = {
        'Question': st.session_state.last_question,
        'Answer': st.session_state.last_answer,
        'Score': mapped_score,
        'Text': response.get('text', '')  # Ensure there's always text, even if it's an empty string
    }
    
    st.session_state.feedback_df = pd.concat([st.session_state.feedback_df, pd.DataFrame([feedback_data])], ignore_index=True)

    # Reset feedback key for next interaction
    st.session_state.fbk = str(uuid.uuid4())

# Generate a unique filename with date, time, and random characters
def generate_filename():
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
    filename = f"feedback_{current_time}_{random_chars}.csv"
    return filename

# Header
st.header("Smart Search")

# Sidebar with instructions
with st.sidebar:
    st.markdown("""# Instructions""")
    st.markdown("""
Search customer frequently asked questions. 

For example:
- How can I fund my account?
- Where can I log in to MyAccount?
- How to trade?
    
This search engine does not look at the open internet to answer these questions - to create an answer, it searches for related content against documents obtained from our website. If the results do not contain any relevant information, the engine will respond: I don't know.
    """)

# Input fields
coli1, coli2 = st.columns([3, 1])
with coli1:
    question = st.text_input("Ask a question:", value="")
with coli2:
    language = st.selectbox('Answer language', ('English', 'Spanish', 'French', 'German', 'Portuguese', 'Italian'), index=0)

# Search button
button = st.button('Search')

# Check if search button is clicked
if button:
    if not question:
        st.error("Please enter a question!")
    else:
        # Store the question and reset feedback state
        st.session_state.last_question = question
        st.session_state.feedback_given = False

        # Generate and display the answer
        answer = response_generator()
        st.session_state.last_answer = answer

        # Store the search results in session state
        st.session_state.search_results = [
            {
                "title": f"Example Document {i+1}",
                "score": round(random.uniform(75, 100), 2),
                "summary": "This is a summary of the document content."
            }
            for i in range(3)
        ]

# Display the answer and search results if available
if st.session_state.last_answer:
    st.subheader("Answer")
    display_answer(st.session_state.last_answer)
    st_copy_to_clipboard(st.session_state.last_answer, key="answer_clipboard")

    # Feedback section just below the answer
    if not st.session_state.feedback_given:
        streamlit_feedback(
            feedback_type="thumbs",
            optional_text_label="[Was this helpful? Why?]",
            align="flex-start",
            key=st.session_state.fbk,
            on_submit=fbcb
        )

if st.session_state.search_results:
    st.subheader("Search Results")
    for i, result in enumerate(st.session_state.search_results):
        st.markdown(f"[{result['title']}](#)  (Score: {result['score']}%)")
        st.markdown(result['summary'])
        st_copy_to_clipboard(result['summary'], key=f"summary_clipboard_{i}")
        st.markdown("---")

# End Session Button
if st.button("End Session"):
    st.subheader("Feedback Summary")
    st.dataframe(st.session_state.feedback_df)
