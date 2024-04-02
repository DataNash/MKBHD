import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def set_plot_style():
    # Set the background color to transparent and text to white
    plt.rcParams['figure.facecolor'] = 'none'
    plt.rcParams['axes.facecolor'] = 'none'
    plt.rcParams['axes.edgecolor'] = 'white'
    plt.rcParams['axes.labelcolor'] = 'white'
    plt.rcParams['xtick.color'] = 'white'
    plt.rcParams['ytick.color'] = 'white'
    plt.rcParams['text.color'] = 'white'
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.right'] = False
    plt.rcParams['axes.spines.left'] = True
    plt.rcParams['axes.spines.bottom'] = True
    

def createStreamLitChart(df, column):
    if column == 'Scaled Sentiment':
        x=df['Scaled Sentiment'].value_counts()
        order = ['Positive', 'Neutral', 'Negative'] 
        colors = ["green", "orange", "red"]
       # st.bar_chart(x)
        set_plot_style()
        plt.figure(figsize=(10, 6))
        sns.barplot(x=x.index, y=x.values, order=order, palette=colors)
        # Setting the background color to transparent and text to white
        
        # Adding titles and labels for clarity
        plt.title('Sentiment Distribution', color='white', fontweight='bold')
        plt.xlabel('Frequency', color='white', fontweight='bold')
        plt.ylabel('Count', color='white', fontweight='bold')
        # Display the plot in Streamlit
        st.pyplot(plt)

    if column == "emotion":
        x=df['emotion'].value_counts()
        set_plot_style()
        plt.figure(figsize=(10, 6))
        sns.barplot(x=x.index, y=x.values,color='#ffd31c')
        # Setting the background color to transparent and text to white
        set_plot_style()
        # Adding titles and labels for clarity
        plt.title('Emotion Distribution', color='white', fontweight='bold')
        plt.xlabel('Emotion', color='white')
        plt.ylabel('Requency', color='white')
        # Display the plot in Streamlit
        st.pyplot(plt)

    if column == "theme":
        x=df['theme'].value_counts()
        set_plot_style()
        plt.figure(figsize=(10, 6))
        sns.barplot(x=x.index, y=x.values,color='#ffd31c')
        # Setting the background color to transparent and text to white
        set_plot_style()
        # Adding titles and labels for clarity
        plt.title('Time Spent Talking About', color='white', fontweight='bold')
        plt.xlabel('Theme', color='white', fontweight='bold')
        plt.ylabel('Number of Comments About', color='white', fontweight='bold')
        # Display the plot in Streamlit
        st.pyplot(plt)
        
    if column == "Sentiment Number":
        set_plot_style()
        plt.plot(df['batch_counter'], df['Sentiment Number'], marker='o', color='#ffd31c', markerfacecolor='white', markeredgecolor='white')
        plt.axis([None,None,0,5])
        plt.title(f'Sentiment Development')
        plt.xlabel('Time', fontweight='bold')
        plt.ylabel('Sentiment', fontweight='bold')

        # Display the plot in Streamlit
        st.pyplot(plt)

    if column == 'batch_text':
        df = df[['batch_text', 'emotion', 'theme']]
        use_container_width = st.checkbox("Use container width", value=False, key="use_container_width")
        st.dataframe(df, use_container_width=use_container_width)
