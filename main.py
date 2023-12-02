from flask import Flask, jsonify, request
import markovify, requests

app = Flask(__name__)

def getAccountID(username):
    return requests.get(f'https://gdbrowser.com/api/profile/{username}').json().get('accountID') if r.status_code == 200 else None

def generate(model, chars):
    retries, sentence = 0, None
    
    while not sentence and retries < 10:
        sentence = model.make_short_sentence(chars)
        retries += 1

    return sentence

@app.route('/', methods=['GET'])
def endpoints():
    endpoints = {
        'GET /comments': {
            'parameters': {
                'id': 'Target Level ID',
                'characters': 'Maximum characters to generate (min: 20, max: 200, default: 40)'
            },
            'description': 'Generate a sentence based on Geometry Dash Comments'
        },
        'GET /posts': {
            'parameters': {
                'username': 'Target Geometry Dash Username',
                'characters': 'Maximum characters to generate (min: 20, max: 200, default: 40)'
            },
            'description': 'Generate a sentence based on Geometry Dash Profile Posts'
        }
    }

    return jsonify(endpoints)

def get_info(url, chars):
    vsauce = request.args.get('id') or request.args.get('username')
    if vsauce is None:
        return jsonify({'error': f'Please provide the "{url}" parameter.'}), 400

    response = requests.get(f'https://gdbrowser.com/api/{url}/{vsauce}?count=100')

    if response.status_code != 200:
        return jsonify({'error': f'Failed to fetch {url} from GDBrowser API.'}), 500

    data = response.json()
    smoke_weed = [comment.get('content', '') for comment in data]
    sentence = generate(markovify.Text(smoke_weed), chars)
    return jsonify({'sentence': sentence})

@app.route('/comments', methods=['GET'])
def get_comments():
    return get_info('comments', int(request.args.get('characters', 40)))

@app.route('/posts', methods=['GET'])
def get_posts():
    return get_info('comments', int(request.args.get('characters', 40)))

if __name__ == '__main__':
    app.run(debug=True)
