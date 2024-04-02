import pandas as pd
def readDataFromExcel(pathToFile):
    pathToFile = rf'{pathToFile}'
    targetFile = pd.read_excel(pathToFile)
    mainDf = targetFile.rename(columns={'Phone':'Make'})
    mainDf['Phone'] = mainDf['Brand'].astype(str) + " " + mainDf['Make'].astype(str)

def IDFromLink(url):
    # Check if 'v=' is in the URL
    if 'v=' in url:
        # Split the URL at 'v=' and take the second part
        start = url.split('v=')[1]

        # The video ID is everything up to the first '&' character
        video_id = start.split('&')[0]
        return video_id
    else:
        return "No video ID found in the URL"


def userinput():
    Link = input("What's the video link: ")
    Brand = input("What is the brand of the phone e.g. Samsung: ")
    Phone = input("Whats the specific phone e.g. S23 Ultra: ")

    videoID = IDFromLink(Link)
    dfData = {
        'Link': [Link],
        'VideoID': [videoID],
        'Brand': [Brand],
        'Phone': [Phone]
    }

    df = pd.DataFrame(dfData)
    print(df)
    return df