import pandas as pd
from flask import Flask, render_template, request
from analysis import analyze_reviews, analyze_time, analyze_courses, course_suggestion
import google.generativeai as genai # Ensure this line is correct

app = Flask(__name__)

def generate_feedback_with_model(review_rating, average_stay, course_completion_percentage, api_key):
    # Configure Google Generative AI
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")

    # Prepare the prompt for feedback
    prompt = f"""
    Given the following employee performance metrics:
    - Review Rating: {review_rating}
    - Average Stay Time: {average_stay} hours
    - Course Completion Percentage: {course_completion_percentage}%

    Please provide a two-line feedback on areas for improvement and any strengths.
    """

    # Generate feedback
    response = model.generate_content(prompt)
    feedback = response.text.strip()  # Get the generated feedback

    return feedback

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def results():
    name = request.form['name']
    review_rating = None
    average_stay = None
    stay_percentage = None
    course_completion_percentage = None

    df_analyzed, df_cleaned = analyze_reviews("Untitled spreadsheet.xlsx", "Your API KEY")
    
    if name in df_analyzed['Name'].values:
        review_rating = df_analyzed.loc[df_analyzed['Name'] == name, 'final_rating'].values[0]
        review_rating = round(review_rating, 2) 
    else:
        review_rating = "Name not found."
    
    if review_rating=="Name not found.":
        average_stay=0.0
        stay_percentage=0.0
    else:
        average_stay, stay_percentage = analyze_time(df_cleaned)
        df_cleaned = analyze_courses(df_cleaned)
    
    if name in df_cleaned['Name'].values:
        course_completion_percentage = df_cleaned.loc[df_cleaned['Name'] == name, 'courses_completed_percentage'].values[0]

    average_stay = round(average_stay, 2)  # Round average stay to 2 decimal places
    stay_percentage = round(stay_percentage, 2)  # Round stay percentage to 2 decimal places

    if course_completion_percentage is not None:
        course_completion_percentage = round(course_completion_percentage, 2)
    else:
        course_completion_percentage = 0.0  # or any default value you see fit
    
    api_key = "Your API KEY"  # Use your actual API key here
    feedback = generate_feedback_with_model(review_rating, average_stay, course_completion_percentage, api_key)

    return render_template('metrics.html', review_rating=review_rating, average_stay=average_stay,
                           stay_percentage=stay_percentage, course_completion_percentage=course_completion_percentage, name=name, feedback=feedback)

@app.route('/dashboard',methods=['POST'])
def dashboard():
    name = request.form['name']
    review_rating = None
    average_stay = None
    stay_percentage = None
    course_completion_percentage = None
    course_list = None 

    df_analyzed, df_cleaned = analyze_reviews("Untitled spreadsheet.xlsx", "Your API KEY")
    
    if name in df_analyzed['Name'].values:
        review_rating = df_analyzed.loc[df_analyzed['Name'] == name, 'final_rating'].values[0]
        review_rating = round(review_rating, 2) 
    else:
        review_rating = "Name not found."
    
    if review_rating=="Name not found.":
        average_stay=0.0
        stay_percentage=0.0
    else:
        average_stay, stay_percentage = analyze_time(df_cleaned)
        df_cleaned = analyze_courses(df_cleaned)
    
    if name in df_cleaned['Name'].values:
        course_completion_percentage = df_cleaned.loc[df_cleaned['Name'] == name, 'courses_completed_percentage'].values[0]

    average_stay = round(average_stay, 2)  # Round average stay to 2 decimal places
    stay_percentage = round(stay_percentage, 2)  # Round stay percentage to 2 decimal places

    if course_completion_percentage is not None:
        course_completion_percentage = round(course_completion_percentage, 2)
    else:
        course_completion_percentage = 0.0  # or any default value you see fit
    
    api_key = "Your API KEY"  # Use your actual API key here
    feedback = generate_feedback_with_model(review_rating, average_stay, course_completion_percentage, api_key)
 
    df_suggestion = course_suggestion("Untitled spreadsheet.xlsx","Your API KEY")
    
    if name in df_suggestion['Name'].values:
        course_list = df_suggestion.loc[df_suggestion['Name'] == name, 'course_suggestion'].values[0]
    
    if course_list is not None:
        course_list=course_list
    else:
        course_list="No Course To List"

    # You can render any specific data you want on this dashboard
    return render_template('dashboard.html', review_rating=review_rating, average_stay=average_stay,
                           stay_percentage=stay_percentage, course_completion_percentage=course_completion_percentage, name=name, feedback=feedback,course_list=course_list)

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=5001)


