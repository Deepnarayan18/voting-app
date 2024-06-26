from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# In-memory data structure to store users and votes
users = {}
votes = {}

# Read candidates from file
with open('candidates.txt', 'r') as f:
    candidates = [line.strip() for line in f.readlines()]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash('Username and password cannot be empty!', 'error')
        elif username in users:
            flash('Username already exists!', 'error')
        else:
            users[username] = {'password': password, 'has_voted': False}
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash('Username and password cannot be empty!', 'error')
        elif username in users and users[username]['password'] == password:
            session['user_id'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('vote'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if 'user_id' not in session:
        flash('You need to log in to vote!', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']
    if users[user_id]['has_voted']:
        flash('You have already voted!', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        selected_candidate = request.form.get('candidate')
        if not selected_candidate:
            flash('Please select a candidate!', 'error')
        else:
            votes[user_id] = selected_candidate
            users[user_id]['has_voted'] = True
            flash('Vote cast successfully!', 'success')
            return redirect(url_for('index'))

    return render_template('vote.html', candidates=candidates) 

@app.route('/results')
def results():
    vote_counts = {candidate: 0 for candidate in candidates}
    for vote in votes.values():
        vote_counts[vote] += 1

    sorted_candidates = sorted(vote_counts.items(), key=lambda item: item[1], reverse=True)
    winner = sorted_candidates[0]
    losers = sorted_candidates[1:]

    return render_template('results.html', winner=winner, losers=losers, vote_counts=vote_counts)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
