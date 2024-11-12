import pandas as pd
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment import SentimentIntensityAnalyzer
import google.generativeai as genai
import json

def analyze_reviews(file_path, api_key):
    # Load data
    df = pd.read_excel(file_path)
    df_cleaned = df.dropna()

    # Initialize sentiment analyzer
    sia = SentimentIntensityAnalyzer()

    # Define sentiment scoring function
    def get_sentiment_scores(text):
        scores = sia.polarity_scores(text)
        return scores

    # Create a DataFrame for reviews
    df1 = pd.DataFrame()
    df1['reviews'] = df_cleaned['review_text']
    df1['Name'] = df_cleaned['Name']

    # Apply sentiment analysis
    df1['SentimentScores'] = df1['reviews'].apply(get_sentiment_scores)
    df1['Compound'] = df1['SentimentScores'].apply(lambda x: x['compound'])

    # Prepare data for JSON
    new = df1[['Name', 'reviews', 'Compound']]
    df_json_zero = new.to_json(orient='records')

    # Configure Google Generative AI
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")

    # Prompt for sentiment rating
    prompt_zero = f"""You are an expert in sentiment analysis, skilled at rating customer reviews based on their sentiment scores.
    Your task is to assign a sentiment rating to the customer reviews provided between three backticks. The ratings should range from 0 to 10, where:
    - 0 indicates a highly negative sentiment,
    - 10 indicates a highly positive sentiment.

    The customer reviews are provided in JSON format, and your output should only include the JSON code with the updated 'sentiment_rating' values. Please do not change the JSON code format.
    {df_json_zero}
    """

    # Generate content
    response_zero = model.generate_content(prompt_zero)
    response_data_zero = pd.DataFrame(json.loads(response_zero.text.strip("")))

    # Add manager rating and final rating
    response_data_zero['manager_rating'] = df_cleaned['manager_rating'].values*2
    
    response_data_zero['final_rating'] = response_data_zero['sentiment_rating'] + response_data_zero['manager_rating']
    
    response_data_zero['final_rating'] = response_data_zero['final_rating'].values/2
    return response_data_zero, df_cleaned

def analyze_time(df_cleaned):
    # Convert 'check-In' and 'check-Out' to datetime
    df_cleaned['check-In'] = pd.to_datetime(df_cleaned['check-In'], dayfirst=True, errors='coerce')
    df_cleaned['check-Out'] = pd.to_datetime(df_cleaned['check-Out'], dayfirst=True, errors='coerce')

    # Calculate duration in hours
    df_cleaned['Duration'] = (df_cleaned['check-Out'] - df_cleaned['check-In']).dt.total_seconds() / 3600
    average_stay = df_cleaned['Duration'].mean()
    
    # Calculate the percentage of average stay compared to 9 hours
    average_stay_percentage = (average_stay / 9) * 100

    return average_stay, average_stay_percentage

def analyze_courses(df_cleaned):
    # Fill NaN values with 0
    df_cleaned['courses_completed'] = df_cleaned['courses_completed'].fillna(0)

    # Define total courses available
    total_courses = 5

    # Calculate percentage of courses completed
    df_cleaned['courses_completed_percentage'] = (df_cleaned['courses_completed'] / total_courses * 100)
     
    return df_cleaned

def course_suggestion(file_path,api_key):
    df2 = pd.read_excel(file_path)
    df_cleaned1 = df2.dropna()
    if 'course_list' in df_cleaned1.columns:
        df_cleaned1['course_list'] = df_cleaned1['course_list'].apply(lambda x: [course.strip() for course in x.split('\n')] if isinstance(x, str) else [])

    df3 = pd.DataFrame()
    df3['Name'] = df_cleaned1['Name']
    df3['course_list']=df_cleaned1['course_list']

    new3 = df3[['Name','course_list']]
    df_json_two = new3.to_json(orient='records')

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")

    prompt = f"""
    Given the following list of courses completed by an employee in json format
    {df_json_two}
    
    Please suggest the next course(s) that the employee should take to further enhance their skills. 
    and your output should only include the JSON code with the updated 'course_suggestion' values. Please do not change the JSON code format
    """

    response_two = model.generate_content(prompt)
    response_data_two = pd.DataFrame(json.loads(response_two.text.strip("")))

    return response_data_two