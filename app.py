from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf import CSRFProtect
import json
import os
import pandas as pd

app = Flask(__name__)

# Secret key for CSRF protection (make sure it's set as an environment variable in PythonAnywhere)
app.secret_key = os.getenv("SECRET_KEY")

# Enable CSRF protection globally for the app
csrf = CSRFProtect(app)

# Load users from JSON
try:
    with open('users.json') as f:
        users = json.load(f)
except FileNotFoundError:
    app.logger.error("users.json file not found")
    users = {}

# Load or initialize annotations
if os.path.exists('annotations.json'):
    with open('annotations.json') as f:
        annotations = json.load(f)
else:
    annotations = []

# Load the title mapping using pandas
def load_title_mapping():
    try:
        df = pd.read_csv('original_to_formatted_titles.csv')
        mapping = pd.Series(df['original_title'].values, index=df['formatted_title']).to_dict()
        return mapping
    except FileNotFoundError:
        app.logger.error("original_to_formatted_titles.csv file not found")
        return {}

# Load similarity matrix
def load_similarity_matrix():
    try:
        return pd.read_csv('similarity_matrix.csv')
    except FileNotFoundError:
        app.logger.error("similarity_matrix.csv file not found")
        return pd.DataFrame()

# Load the mapping globally
title_mapping = load_title_mapping()
similarity_matrix = load_similarity_matrix()

# Helper to load poems
def get_poem_text(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        app.logger.error(f"Poem file {path} not found")
        return None

# Helper to get annotated poems for a user
def get_annotated_poems(username):
    user_annotations = [annotation['poem'] for annotation in annotations if annotation['user'] == username]
    return user_annotations

# Helper to get assigned poems for a user
def get_assigned_poems(username):
    return users.get(username, {}).get('assigned_poems', [])

# Helper to get recommendations from the similarity matrix (only top 10)
def get_recommendations(poem_key):
    try:
        row = similarity_matrix[similarity_matrix['poem'] == poem_key]
        if not row.empty:
            recommendations = row.iloc[0, 1:11].tolist()  # Get top 10 recommendations
            return recommendations
    except Exception as e:
        app.logger.error(f"Error fetching recommendations for {poem_key}: {e}")
    return []

# Find the first non-annotated poem for the user and redirect to it
@app.route('/start_annotation')
def start_annotation():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    assigned_poems = get_assigned_poems(username)
    annotated_poems = get_annotated_poems(username)
    
    # Find the first unannotated poem in the assigned list
    for poem_key in assigned_poems:
        if poem_key not in annotated_poems:
            # Redirect to the annotation page for this poem
            poem_url = poem_key.replace('/', '__').replace('.pt', '')
            return redirect(url_for('annotate', poem_url=poem_url))
    
    # If all poems are annotated, return to instructions or display a message
    return redirect(url_for('instructions'))

# Home page
@app.route('/')
def home():
    return render_template('home.html')

# Helper to format author and title
def format_author_title(poem_key):
    author, formatted_title = poem_key.split('/')
    
    # Capitalize the author (replace hyphens with spaces and capitalize each word)
    author = author.replace('-', ' ').title()
    
    # Convert formatted title back to the original title, remove .pt, and format properly
    formatted_title = formatted_title.replace('.pt', '').replace('-', ' ').title()
    
    return author, formatted_title

@app.route('/instructions')
def instructions():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']

    # Get the list of assigned and annotated poems
    assigned_poems = get_assigned_poems(username)
    annotated_poems = get_annotated_poems(username)

    # Separate poems into annotated and unannotated lists
    unannotated_poems = [poem for poem in assigned_poems if poem not in annotated_poems]
    annotated_poems_list = [poem for poem in assigned_poems if poem in annotated_poems]

    # Pass this data to the template, format author and title
    unannotated_poems_formatted = [format_author_title(poem) for poem in unannotated_poems]
    annotated_poems_formatted = [format_author_title(poem) for poem in annotated_poems_list]

    # Pass the formatted data to the template
    return render_template('instructions.html', 
                           unannotated_poems=unannotated_poems_formatted, 
                           annotated_poems=annotated_poems_formatted)

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('instructions'))  # Redirect to instructions page after login
        else:
            return render_template('login.html', error='Credenciales inválidas')
    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

# Annotation page
@app.route('/annotate/<poem_url>', methods=['GET', 'POST'])
def annotate(poem_url):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Reconstruct the poem_key from the poem_url
    poem_key = poem_url.replace('__', '/') + '.pt'
    
    # Get annotated poems for this user
    annotated_poems = get_annotated_poems(session['username'])
    
    # Check if the current poem has already been annotated by this user
    if poem_key in annotated_poems:
        return redirect(url_for('instructions'))  # Redirect to instructions if already annotated
    
    # Check if the poem is assigned to the user
    assigned_poems = get_assigned_poems(session['username'])
    if poem_key not in assigned_poems:
        return "Error: Poema no asignado a este usuario", 403  # Forbidden
    
    # Split the poem_key into author and formatted title
    author, formatted_title = poem_key.split('/')
    
    # Format the author name properly (capitalize and replace hyphens with spaces)
    author_formatted = author.replace('-', ' ').title()
    
    app.logger.info(f"Author: {author_formatted}, Formatted title: {formatted_title}")
    
    # Remove .pt and replace with .txt
    formatted_title = formatted_title.replace('.pt', '.txt')
    
    # Look up the corresponding original title using the mapping
    original_title = title_mapping.get(formatted_title)
    if not original_title:
        return "Error: Poema no encontrado en el mapeo", 404
    
    # Construct the path to the original poem file
    poem_path = os.path.join('corpus', author, f"{original_title}.txt")
    poem_text = get_poem_text(poem_path)
    if poem_text is None:
        return "Error: No se pudo cargar el texto del poema", 404

    # Load the top 10 recommended poems' text from similarity matrix
    recommendations = get_recommendations(poem_key)
    recommendation_texts = {}

    for rec in recommendations:
        rec_author, rec_formatted_title = rec.split('/')
        rec_formatted_title = rec_formatted_title.replace('.pt', '.txt')
        rec_original_title = title_mapping.get(rec_formatted_title)
        
        if rec_original_title:
            rec_path = os.path.join('corpus', rec_author, f"{rec_original_title}.txt")
            rec_text = get_poem_text(rec_path)
            recommendation_texts[rec] = rec_text or "Error: No se encontró el poema."
        else:
            recommendation_texts[rec] = "Error: Poema no encontrado en el mapeo."

    if request.method == 'POST':
        labels = {rec: request.form.get(rec) for rec in recommendations}
        # Ensure all recommendations have a value before submitting
        if None in labels.values():
            return render_template(
                'annotate.html',
                author=author_formatted,
                original_title=original_title,
                poem_text=poem_text,
                poem=poem_key,
                recommendations=recommendations,
                recommendation_texts=recommendation_texts,
                title_mapping=title_mapping,
                error="Por favor, selecciona una opción para todos los poemas recomendados."
            )
        
        annotation = {
            'user': session['username'],
            'poem': poem_key,
            'labels': labels
        }
        annotations.append(annotation)
        with open('annotations.json', 'w') as f:
            json.dump(annotations, f, indent=4)
        return redirect(url_for('annotate', poem_url=poem_url))

    # Render the original poem with its original title and the recommended poems' text
    return render_template(
        'annotate.html',
        author=author_formatted,  # Pass the formatted author to the template
        original_title=original_title,  # Pass the formatted title
        poem_text=poem_text, 
        poem=poem_key, 
        recommendations=recommendations, 
        recommendation_texts=recommendation_texts,
        title_mapping=title_mapping  # Pass title_mapping to the template
    )


if __name__ == '__main__':
    app.run(debug=True)

