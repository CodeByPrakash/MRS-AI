from flask import Flask, render_template, request
import wikipediaapi

app = Flask(__name__, template_folder='.')

# Function to fetch Wikipedia summary
def get_wikipedia_page_summary(page_name):
    wiki_wiki = wikipediaapi.Wikipedia('en-US, en-IN')
    page = wiki_wiki.page(page_name)
    
    if page.exists():
        return page.summary
    else:
        return f"Page '{page_name}' not found."

@app.route('/', methods=['GET', 'POST'])
def index():
    summary = ""
    if request.method == 'POST':
        page_name = request.form['page_name']
        summary = get_wikipedia_page_summary(page_name)
    
    return render_template('index1.html', summary=summary)

if __name__ == '__main__':
    app.run(debug=True)
