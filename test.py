from flask import Flask, render_template
app = Flask(__name__, template_folder='.') 
@app.route("/")
def hello():
    return render_template('index2.html') #"Hello World!"

if __name__ == "__main__":
    app.run()