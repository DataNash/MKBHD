import warnings
import pandas as pd
# Suppress all warnings
warnings.filterwarnings('ignore')
from processVideos.getVideoDetails import videoMetaData
from transcriptProcessing.transcript import punctuate_transcripts_in_dataframe
from sentimentXthemes.reviewTheme import getThemeAndSentiment, flattenPredictions
from Visualisations.Visualisations import createStreamLitChart, ChangeButtonColour

def assessLinks(linkOrLinks, Brand=None, Phone=None):
    metadata = videoMetaData(linkOrLinks)
    punctuatedTranscript = punctuate_transcripts_in_dataframe(metadata)
    punctuatedTranscript['semantically_replaced_transcript']  = punctuatedTranscript['semantically_replaced_transcript'].astype(str)
    punctuatedTranscript['predictions'] = punctuatedTranscript['semantically_replaced_transcript'].apply(getThemeAndSentiment)
    finalDF = flattenPredictions(punctuatedTranscript)
    if Brand and Phone is None:
        pass    
    else :
        finalDF['Brand'] = Brand
        finalDF['Phone'] = Phone
    return finalDF

import streamlit as st
st.set_page_config(layout="wide")
st.subheader("Instructions")
st.write("1. Input the link to any MKBHD review*")
st.write("2. Input the Brand of the phone and the specific make.")
st.write("3. Hit 'Assess Link' and wait until the balloons appear (~30s)")
st.write("4. Hit on of the buttons e.g. 'Sentiment Analysis' to explore results")
st.write("*To compare 2 phones in a 'versus' mode input a link, brand and make into the secondary boxes.")


linkColumn, brandColumn, makeColumn = st.columns(3)

with linkColumn:
    linkInput = st.text_input(
        "Enter the full link 👇",
        value = "https://www.youtube.com/watch?v=XaqOejIaFgM&pp=ygUFbWtiaGQ%3D"
        #placeholder= "https://www.youtube.com/watch?v=dKq_xfCz3Jk&ab_channel=MarquesBrownlee"
    )
    # linkInput2 = st.text_input("Enter the second video link (optional) 👇", 
    #             value = "https://www.youtube.com/watch?v=0X0Jm8QValY&t=4s&pp=ygUFbWtiaGQ%3D"
    #             #placeholder="https://www.youtube.com/watch?v=..."
    #             )

with brandColumn:
    brandInput = st.text_input(
        "What brand is it? 👇",
        key="Brand",
        value = "Samsung"
        #placeholder= "e.g. ASUS?"
    )
    # brandInput2 = st.text_input(
    #     "What brand is it? 👇",
    #     key="Brand2",
    #     value = "iPhone"
    #     #placeholder= "e.g. Samsung?"
    # )

with makeColumn:
    makeInput = st.text_input(
        "What specific make is it",
        key="make",
        value = "S24 Ultra"
       # placeholder= "E.g. ROG 6"
    )
#     makeInput2 = st.text_input(
#         "What specific make is it",
#         key="make2",
#         value="15 Pro"
# #        placeholder= "E.g. S23 Ultra"
#     )


# Use session state to store which button was pressed
if 'chart_to_show' not in st.session_state:
    st.session_state['chart_to_show'] = None    
    
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


# Initialize session state for the DataFrame and chart to show
if 'dataframe' not in st.session_state:
    st.session_state['dataframe'] = pd.DataFrame()


# Call the function to change the 'Assess Link' button's color and size
  # Make the button text white, background red, and increase the font size for a bigger appearance

col1, col2, col3 = st.columns([1, 2, 1])
ChangeButtonColour('Assess Link', 'white', 'red', '40px')
with col2:
    if st.button('Assess Link'):        
        # Call your function with the user inputs sd
        video_info = [
            {'link': linkInput, 'Brand': brandInput, 'Phone': makeInput}]
        # if linkInput2:  # Add second video info if it exists
        #     video_info.append({'link': linkInput2, 'Brand': brandInput2, 'Phone': makeInput2})
        all_dfs = []
        import time
        
        #st.progress(10)
        with st.spinner('Processing, please be patient. Grab a coffee.'):    
                time.sleep(1)
    
        for video in video_info:        
            df = assessLinks(video['link'], Brand=video['Brand'], Phone=video['Phone'])
            all_dfs.append(df)
        st.session_state['dataframe'] = pd.concat(all_dfs, ignore_index=True)
        st.balloons()
        print(st.session_state['dataframe'])
        
        st.session_state['show_other_buttons'] = True

#ChangeButtonColour('Assess Link', 'white', 'red', '20px') 

if st.session_state.get('show_other_buttons'):
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

    link = 'https://public.tableau.com/app/profile/panashe.mundondo/viz/MKBHDPhoneReviewAnalysis/Story1'
    link_text = "here"  # The text to display as the hyperlink
    full_link = f"[{link_text}]({link})"

    p, graph_col, _ = st.columns([0.4, 1.3, 0.4])  # Adjust the ratio as needed
    with graph_col:
        if st.session_state['chart_to_show'] == 'emotion':
            createStreamLitChart(st.session_state['dataframe'], 'emotion')
            st.write("The above bar chart shows the most frequently occurring emotions in the video.")
            st.markdown(f"To view more aesthetic charts that give more control check out my Tableau dashboard {full_link}.", unsafe_allow_html=True)
        elif st.session_state['chart_to_show'] == 'sentiment_video':
            createStreamLitChart(st.session_state['dataframe'], 'Sentiment Number')
            st.write("The above line chart shows the chronological sentiment development of the video.")
            st.markdown(f"To view more aesthetic charts that give more control check out my Tableau dashboard {full_link}.", unsafe_allow_html=True)
        elif st.session_state['chart_to_show'] == 'pillars':
            createStreamLitChart(st.session_state['dataframe'], 'theme')
            st.write("The above bar chart shows the most frequently occurring topics in the video.")
            st.markdown(f"To view more aesthetic charts that give more control check out my Tableau dashboard {full_link}.", unsafe_allow_html=True)
        elif st.session_state['chart_to_show'] == 'sentiment_analysis':
            createStreamLitChart(st.session_state['dataframe'], 'Scaled Sentiment')
            st.write("The above bar chart shows the most frequently occurring Sentiment in the video.")
            st.markdown(f"To view more aesthetic charts that give more control check out my Tableau dashboard {full_link}.", unsafe_allow_html=True)
        elif st.session_state['chart_to_show'] == 'comments':
            createStreamLitChart(st.session_state['dataframe'], 'batch_text')
            st.write("The above spreadsheet displays the sentences in the script, their assigned emotion and which pillar (if any) it falls under.")
            st.markdown(f"To view more aesthetic charts that give more control check out my Tableau dashboard {full_link}.", unsafe_allow_html=True)

