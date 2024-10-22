from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from scrapper import scrape_linkedin, save_to_csv
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'
scraped_data = []  # Store scraped data in memory

@app.route('/', methods=['GET', 'POST'])
def index():
    global scraped_data  # Store data for rendering and downloading
    if request.method == 'POST':
        query = request.form.get('query')
        num_posts = int(request.form.get('num_posts', 10))

        try:
            scraped_data = scrape_linkedin(query, num_posts)
            save_to_csv(scraped_data, 'linkedin_posts.csv')
            flash('Scraping completed! Data displayed below.', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')

        return redirect(url_for('index'))

    return render_template('index.html', data=scraped_data)

@app.route('/download')
def download():
    csv_path = 'linkedin_posts.csv'
    if os.path.exists(csv_path):
        return send_file(csv_path, as_attachment=True)
    else:
        flash('CSV file not found. Please scrape data first.', 'danger')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
