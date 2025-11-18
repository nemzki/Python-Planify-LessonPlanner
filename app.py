from flask import Flask, render_template, redirect, url_for

#initialize the app
app = Flask(__name__)

#app congiguration

app.config['SECRET_EKY'] = 'planify_secret_key'

#Planify landing page
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/choose-role')
def choose_role():
    return render_template('choose_role.html')

@app.route('/register')
def register():
    return redirect(url_for('choose_role'))

@app.route('/register/<role>')
def role(role):
    return f"Your role: {role}"

if __name__ == '__main__':
    app.run(debug=True)
