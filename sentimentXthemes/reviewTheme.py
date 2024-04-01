from nltk.tokenize import sent_tokenize
from transformers import pipeline, DistilBertTokenizer
from setfit import SetFitModel
import pandas as pd
from transcriptProcessing.transcript import remove_text_inside_brackets

def map_int_to_label(value):
    label_dict = {
        0: 'Battery or Charging',
        1: 'Build quality',
        2: 'Camera',
        3: 'Design',
        4: 'Phone performance',
        5: 'Price',
        6: 'Screen or Display',
        7: 'Unknown'
    }
    return label_dict.get(value, "Unknown")

model = SetFitModel.from_pretrained("datanash/mkbhd5pillars")
sentiment_model = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
emotion_classifier = pipeline(task="text-classification", model="SamLowe/roberta-base-go_emotions")
tokenizer_for_length = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')# Initialize tokenizer for checking token length
transcript_count = 1  # Global variable to keep track of transcripts

def getThemeAndSentiment(transcript):
    
    global transcript_count
    sentences = sent_tokenize(transcript)
    batched_sentences = [sentences[i:i+2] for i in range(0, len(sentences), 2)]
    
    results = []
    batch_count = 0.1
    for batch in batched_sentences:
        combined_text = ' '.join(batch)
        
        # Check token length and adjust if necessary
        tokenized_length = len(tokenizer_for_length.tokenize(combined_text))
        if tokenized_length > 512:
            tokens = tokenizer_for_length.tokenize(combined_text)
            chunks = [tokens[i:i+200] for i in range(0, len(tokens), 200)]
            themes = []
            sentiments = []
            emotions = []
            for chunk in chunks:
                chunk_text = tokenizer_for_length.convert_tokens_to_string(chunk)
                
                # Print the chunk text being processed
                print(f"Processing chunk: {chunk_text}")
                
                # Predict theme
                theme_pred = model([chunk_text])  
                themes.append(map_int_to_label(theme_pred[0].item()))

                # Predict sentiment
                sentiments.append(sentiment_model(chunk_text)[0]['label'])

                # Predict emotion
                emotions.append(emotion_classifier(chunk_text)[0]['label'])
            
            # Using mode (most frequent) theme, sentiment, and emotion for the entire batch
            theme = max(set(themes), key=themes.count)
            sentiment = max(set(sentiments), key=sentiments.count)
            emotion = max(set(emotions), key=emotions.count)
        else:
            # Print the batch text being processed
            print(f"Processing: {combined_text}")
            
            # Predict theme
            theme_pred = model([combined_text])
            theme = map_int_to_label(theme_pred[0].item())
            
            # Predict sentiment
            sentiment = sentiment_model(combined_text)[0]['label']

            # Predict emotion
            emotion = emotion_classifier(combined_text)[0]['label']
        
        results.append({
            'batch_text': remove_text_inside_brackets(combined_text),
            'theme': theme,
            'sentiment': sentiment,
            'emotion': emotion
        })
        
        # Print counts for tracking
        print(f"Finished processing transcript {transcript_count} - batch {round(transcript_count + batch_count, 1)}")
        
        batch_count += 0.1
    
    transcript_count += 1
    return results

def extract_sentiment(sentiment_str):
    return int(sentiment_str[0])

def scale_sentiment(number):
    """
    Scale sentiment based on the number.
    - 1 or 2: Negative
    - 3: Neutral
    - 4 or 5: Positive

    :param number: An integer representing the sentiment score.
    :return: A string representing the scaled sentiment.
    """
    if number in [1, 2]:
        return "Negative"
    elif number == 3:
        return "Neutral"
    elif number in [4, 5]:
        return "Positive"
    else:
        return "Invalid"

def flattenPredictions(df):
    # Initialize a list to hold the flattened data
    flat_data = []

    # Loop through each row of the DataFrame to extract predictions
    for idx, row in df.iterrows():
        video_id = row['videoId']
        for pred in row['predictions']:
            batch_text = pred['batch_text']
            theme = pred['theme']
            sentiment = pred['sentiment']
            emotion = pred['emotion']
            flat_data.append([video_id, batch_text, theme, sentiment,emotion])

    # Convert the flattened list to a DataFrame
    final_df = pd.DataFrame(flat_data, columns=['videoId', 'batch_text', 'theme', 'sentiment', 'emotion'])

    # Add the batch_counter
    final_df['batch_counter'] = final_df.groupby('videoId').cumcount() + 1 
    final_df['Sentiment Number'] = final_df['sentiment'].apply(extract_sentiment)
    final_df['Scaled Sentiment'] = final_df['Sentiment Number'].apply(scale_sentiment)

    #final_df['Sentiment Number'] = final_df['Sentiment Number'].astype(int)
    return final_df






