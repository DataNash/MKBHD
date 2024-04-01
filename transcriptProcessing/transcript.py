import pandas as pd
import numpy as np
import torch
import ast
from transformers import DistilBertTokenizerFast, DistilBertForTokenClassification
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow logging (1: INFO, 2: WARNING, 3: ERROR)

# Now initialize TensorFlow or import your TensorFlow-based module


# Initialize the DistilBert model and tokenizer for punctuation
checkpoint = "unikei/distilbert-base-re-punctuate"
tokenizer = DistilBertTokenizerFast.from_pretrained(checkpoint)
model = DistilBertForTokenClassification.from_pretrained(checkpoint)
encoder_max_length = 256

import re

def remove_text_inside_brackets(text):
    """
    Remove text inside brackets (including the brackets themselves) for all types of brackets: [], (), {}.

    :param text: The input string from which the text inside brackets will be removed.
    :return: A string with the text inside brackets removed.
    """
    text = re.sub(r'\[.*?\]', '', text)  # Remove square brackets and their contents
    text = re.sub(r'\(.*?\)', '', text)  # Remove parentheses and their contents
    text = re.sub(r'\{.*?\}', '', text)  # Remove curly brackets and their contents
    return text


def extract_plain_text_from_transcript(transcript_list):
    """
    Extract plain text from a list of transcript dictionaries.
    
    - str: Concatenated plain text.
    """
    plainText = []
    for dictionary in transcript_list:
        for key, value in dictionary.items():
            if key == 'text':
                plainText.append(value)
                plainText.append(' ')
    return ''.join(plainText)

def split_to_segments(wrds, length, overlap):
    """
    Split the words into segments of a specified length with a specified overlap.
    Returns:
    - list: List of segments (dictionaries) with text and start/end indices.
    """
    resp = []
    i = 0
    while True:
        wrds_split = wrds[(length * i):((length * (i + 1)) + overlap)]
        if not wrds_split:
            break
        resp_obj = {
            "text": wrds_split,
            "start_idx": length * i,
            "end_idx": (length * (i + 1)) + overlap,
        }
        resp.append(resp_obj)
        i += 1
    return resp

def punctuate_wordpiece(wordpiece, label):
    """
    Punctuate a wordpiece based on its label.
    Returns:
    - str: Punctuated wordpiece.
    """
    if label.startswith('UPPER'):
        wordpiece = wordpiece.upper()
    elif label.startswith('Upper'):
        wordpiece = wordpiece[0].upper() + wordpiece[1:]
    if label[-1] != '_' and label[-1] != wordpiece[-1]:
        wordpiece += label[-1]
    return wordpiece

def punctuate_segment(wordpieces, word_ids, labels, start_word):
    """
    Punctuate a segment of wordpieces based on their labels.
    - start_word (int): Word ID to start from.
    Returns:
    - str: Punctuated text segment.
    """
    result = ''
    for idx in range(0, len(wordpieces)):
        if word_ids[idx] == None:
            continue
        if word_ids[idx] < start_word:
            continue
        wordpiece = punctuate_wordpiece(wordpieces[idx][2:] if wordpieces[idx].startswith('##') else wordpieces[idx],
                                        labels[idx])
        if idx > 0 and len(result) > 0 and word_ids[idx] != word_ids[idx - 1] and result[-1] != '-':
            result += ' '
        result += wordpiece
    return result

def process_segment(words, tokenizer, model, start_word):
    """
    Tokenize, predict punctuation, and punctuate a text segment.
    Parameters:
    - words (dict): Dictionary with the text segment and start/end indices.
    - tokenizer (DistilBertTokenizerFast): Tokenizer for text processing.
    - model (DistilBertForTokenClassification): Model for punctuation prediction.
    - start_word (int): Word ID to start from.
    Returns:
    - str: Punctuated text segment.
    """
    tokens = tokenizer(words['text'],
                       padding="max_length",
                       max_length=encoder_max_length,
                       is_split_into_words=True, return_tensors='pt')
    
    with torch.no_grad():
        logits = model(**tokens).logits
    logits = logits.cpu()
    predictions = np.argmax(logits, axis=-1)
    wordpieces = tokens.tokens()
    word_ids = tokens.word_ids()
    id2label = model.config.id2label
    labels = [[id2label[p.item()] for p in prediction] for prediction in predictions][0]
    return punctuate_segment(wordpieces, word_ids, labels, start_word)

def punctuate(text, tokenizer, model):
    """
    Punctuate text of any length.
    Parameters:
    - text (str): Text to punctuate.
    - tokenizer (DistilBertTokenizerFast): Tokenizer for text processing.
    - model (DistilBertForTokenClassification): Model for punctuation prediction.
    Returns:
    - str: Punctuated text.
    """
    text = text.lower()
    text = text.replace('\n', ' ')
    words = text.split(' ')
    overlap = 50
    slices = split_to_segments(words, 150, 50)
    result = ""
    start_word = 0
    for text in slices:
        corrected = process_segment(text, tokenizer, model, start_word)
        result += corrected + ' '
        start_word = overlap
    return result

def punctuate_transcript(plainTranscript):
    """
    Punctuate a list of transcript dictionaries.
    Parameters:
    - transcript_list (list): List of transcript dictionaries.
    Returns:
    - str: Punctuated transcript.
    """
    punctuated_version = punctuate(plainTranscript, tokenizer, model)
    return punctuated_version

semantic_dict = {
    'design': ['flat edges'],
    
    'build quality': ['speaker', 'glass'],
    
    'battery': ['fast charge', 'wireless charging', 'drain', 'screen on time', 'usage time'],
    
    'camaera': ['camera', 'lens', 'megapixel', 'MP', 'portrait', 'photo', 'image', 'picture', 'shutter', 'zoom', 'flash', 'low light', 'sensor', 'resolution', 'video', 'optical'],
    
    'screen': ['hz', 'OLED', 'LCD', 'herz', 'nits', 'refresh rate','bezel'],
    
    'performance': ['processor', 'CPU', 'GPU', 'RAM', 'memory', 'storage', 'multitasking']
}

def semantic_replacement(text, semantic_dict):
    for key, values in semantic_dict.items():
        for value in values:
            text = text.replace(value, key)
    return text #perform semantic replacement of key terms that occur often

def punctuate_transcripts_in_dataframe(df):
    """
    Punctuates the transcripts in the 'transcript' column of the given dataframe.
    Parameters:
    - df (pd.DataFrame): DataFrame containing a 'transcript' column.
    Returns:
    - pd.DataFrame: DataFrame with punctuated transcripts.
    """
    df['punctuated_transcript'] = df['transcript'].apply(
        lambda x: punctuate_transcript(extract_plain_text_from_transcript(ast.literal_eval(x))) if x and isinstance(x, str) else None
    )
    df['punctuated_transcript'] = df['punctuated_transcript'].apply(remove_text_inside_brackets)
    df['semantically_replaced_transcript'] = df['punctuated_transcript'].apply(lambda x: semantic_replacement(x, semantic_dict) if isinstance(x, str) else x)
    return df


