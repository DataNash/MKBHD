import warnings

# Suppress all warnings
warnings.filterwarnings('ignore')

# Alternatively, suppress specific types of warnings
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

from processVideos.getVideoDetails import videoMetaData
from transcriptProcessing.transcript import punctuate_transcripts_in_dataframe
from sentimentXthemes.reviewTheme import getThemeAndSentiment, flattenPredictions

def assessLinks(linkOrLinks, Brand=None, Phone=None):
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
    finalDF.to_excel(r'C:\Users\panas\OneDrive\Desktop\DataScience\PersonalProjects\MKBHDModularised\outputS23.xlsx')
    return finalDF

assessLinks('https://www.youtube.com/watch?v=zhoTX0RRXPQ&t=4s&pp=ygUWbWtiaGQgZ2FsYXh5IHMyMyB1bHRyYQ%3D%3D', Brand='Samsung', Phone ='S23 Ultra')