import warnings
import pandas as pd
# Suppress all warnings
warnings.filterwarnings('ignore')
from processVideos.getVideoDetails import videoMetaData
from transcriptProcessing.transcript import punctuate_transcripts_in_dataframe
from sentimentXthemes.reviewTheme import getThemeAndSentiment, flattenPredictions
from Visualisations.Visualisations import createStreamLitChart

def assessLinks(linkOrLinks, Brand=None, Phone=None):
    print("Evidently I am assessing.")
    metadata = videoMetaData(linkOrLinks)
    punctuatedTranscript = punctuate_transcripts_in_dataframe(metadata)
    punctuatedTranscript['semantically_replaced_transcript']  = punctuatedTranscript['semantically_replaced_transcript'].astype(str)
    punctuatedTranscript['predictions'] = punctuatedTranscript['semantically_replaced_transcript'].apply(getThemeAndSentiment)
    finalDF = flattenPredictions(punctuatedTranscript)
    print(finalDF)
    if Brand and Phone is None:
        pass    
    else :
        finalDF['Brand'] = Brand
        finalDF['Phone'] = Phone
    #finalDF.to_excel(r'C:\Users\panas\OneDrive\Desktop\DataScience\PersonalProjects\MKBHDModularised\output.xlsx')
    print("I gave the label bills bills bills.")
    return finalDF

import streamlit as st
st.set_page_config(layout="wide")
linkColumn, brandColumn, makeColumn = st.columns(3)

with linkColumn:
    linkInput = st.text_input(
        "Enter the full link 👇",
        placeholder= "https://www.youtube.com/watch?v=dKq_xfCz3Jk&ab_channel=MarquesBrownlee"
    )
    linkInput2 = st.text_input("Enter the second video link (optional) 👇", 
                placeholder="https://www.youtube.com/watch?v=...")

with brandColumn:
    brandInput = st.text_input(
        "What brand is it? 👇",
        key="Brand",
        placeholder= "e.g. ASUS?"
    )
    brandInput2 = st.text_input(
        "What brand is it? 👇",
        key="Brand2",
        placeholder= "e.g. Samsung?"
    )

with makeColumn:
    makeInput = st.text_input(
        "What specific make is it",
        key="make",
        placeholder= "E.g. ROG 6"
    )
    makeInput2 = st.text_input(
        "What specific make is it",
        key="make2",
        placeholder= "E.g. S23 Ultra"
    )

# Define callback functions for each button
def show_sentiment_video():
    st.session_state['chart_to_show'] = 'sentiment_video'

def show_pillars():
    st.session_state['chart_to_show'] = 'pillars'

def show_emotions():
    st.session_state['chart_to_show'] = 'emotion'

def show_sentiment_analysis():
    st.session_state['chart_to_show'] = 'sentiment_analysis'

def show_comments():
    st.session_state['chart_to_show'] = 'comments'

# Use session state to store which button was pressed
if 'chart_to_show' not in st.session_state:
    st.session_state['chart_to_show'] = None    

# Initialize session state for the DataFrame and chart to show
if 'dataframe' not in st.session_state:
    st.session_state['dataframe'] = pd.DataFrame()
if 'chart_to_show' not in st.session_state:
    st.session_state['chart_to_show'] = None


if st.button('Assess Link'):
    # Call your function with the user inputs sd
    st.session_state['dataframe'] = assessLinks(linkInput, Brand=brandInput, Phone=makeInput)
    print(st.session_state['dataframe'])
    
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.button('Sentiment Development', on_click=show_sentiment_video)
with col2:
    st.button('Pillars', on_click=show_pillars)
with col3:
    st.button('Emotions', on_click=show_emotions)
with col4:
    st.button('Sentiment Analysis', on_click=show_sentiment_analysis)
with col5:
    st.button('Comments', on_click=show_comments)

p, graph_col, _ = st.columns([0.4,1.3, 0.4])  # Adjust the ratio as needed
with graph_col:
    if st.session_state['chart_to_show'] == 'emotion':
        createStreamLitChart(st.session_state['dataframe'], 'emotion')
        st.write("The above bar chart shows the most frequently occuring \n emotions in the video.")
        st.write("To view more aestethic charts that give more control check out my Tableau dashboard {link}.")
    elif st.session_state['chart_to_show'] == 'sentiment_video':
        createStreamLitChart(st.session_state['dataframe'], 'Sentiment Number')
        st.write("The above line chart shows the chronological sentiment development of the video.")
        st.write("To view more aestethic charts that give more control check out my Tableau dashboard {link}.")
    elif st.session_state['chart_to_show'] == 'pillars':
        createStreamLitChart(st.session_state['dataframe'], 'theme')
        st.write("The above bar chart shows the most frequently occuring topics in the video.")
        st.write("To view more aestethic charts that give more control check out my Tableau dashboard {link}.")
    elif st.session_state['chart_to_show'] == 'sentiment_analysis':
        createStreamLitChart(st.session_state['dataframe'], 'Scaled Sentiment')
        st.write("The above bar chart shows the most frequently occuring Sentiment in the video.")
        st.write("To view more aestethic charts that give more control check out my Tableau dashboard {link}.")
    elif st.session_state['chart_to_show'] == 'comments':
        createStreamLitChart(st.session_state['dataframe'], 'batch_text')
        st.write("The above spreadsheet displays the sentences in the script, their assigned emotion and which pillar (if any) it falls under.")
        st.write("To view more aestethic charts that give more control check out my Tableau dashboard {link}.")

