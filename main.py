from flask import Flask, jsonify, request
import markovify, requests, random

app = Flask(__name__)

def getAccountID(username):
    try:
        r = requests.get(f'https://gdbrowser.com/api/profile/{username}').json()
        return r.get('accountID')
    except Exception as e:
        return jsonify({'error': f'Error fetching accountID for the username: {username}.'}), 500

def generate(model, chars):
    retries, sentence = 0, None
    while not sentence and retries < 1000:
        sentence = model.make_short_sentence(chars)
        retries += 1
    return sentence

@app.route('/', methods=['GET'])
def endpoints():
    endpoints = {
        'GET /comments': {
            'parameters': {
                'id': 'Target Level ID',
                'characters': 'Maximum characters to generate (default: 80)'
            },
            'description': 'Generate a sentence based on Geometry Dash Comments'
        },
        'GET /posts': {
            'parameters': {
                'username': 'Target Geometry Dash Username',
                'characters': 'Maximum characters to generate (default: 50)'
            },
            'description': 'Generate a sentence based on Geometry Dash Profile Posts'
        }
    }

    return jsonify(endpoints)

def comments_ai(chars):
    vsauce = request.args.get('id')
    if vsauce is None:
        return jsonify({'error': f'You didnt provide the "id" parameter.'}), 400
    response = requests.get(f'https://gdbrowser.com/api/comments/{vsauce}?count=100')
    if response.status_code != 200:
        return jsonify({'error': f'Failed to fetch comments from GDBrowser API.'}), 500
    data = response.json()
    smoke_weed = [comment.get('content', '') for comment in data]
    sentence = generate(markovify.Text(smoke_weed), chars)
    return jsonify({'sentence': sentence})

def posts_ai(chars):
    vsauce = request.args.get('username')
    if vsauce is None:
        return jsonify({'error': f'You didnt provide the "username" parameter.'}), 400
    response = requests.get(f'https://gdbrowser.com/api/comments/{getAccountID(vsauce)}?type=profile&count=100')
    if response.status_code != 200:
        return jsonify({'error': f'Failed to fetch posts from GDBrowser API.'}), 500
    data = response.json()
    smoke_weed = [comment.get('content', '') for comment in data]
    sentence = generate(markovify.Text(smoke_weed), chars)
    return jsonify({'sentence': sentence})

@app.route('/comments', methods=['GET'])
def get_comments():
    return comments_ai(int(request.args.get('characters', 80)))

@app.route('/posts', methods=['GET'])
def get_posts():
    return posts_ai(int(request.args.get('characters', 50)))

if __name__ == '__main__':
    app.run(debug=True)
