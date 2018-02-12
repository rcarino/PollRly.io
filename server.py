import json

from flask import abort, request, send_from_directory
from flask_api import FlaskAPI, status

from db.pgclient import query, query_one, execute

app = FlaskAPI(__name__, static_folder='static/build')


@app.route('/')
def root():
    return app.send_static_file('index.html')


# Notes:
# 1. Questions may have the same question text and options. Only uniqueness constraint is id.
# 2. Options and question text have immutability enforced at the app layer. Hence only POST.
# 3. To modify a question, a user is expected to DELETE the old one and create a new updated one
# 4. Deleted/modified questions will lose prior vote data
# 5. App layer enforces there are no duplicates in given options
@app.route('/api/questions', methods=['GET', 'POST'])
def questions_list():
    if request.method == 'POST':
        options = request.data.get('options')
        if type(options) != list or len(options) < 1 or any(map(lambda o: type(o) != str, options)):
            abort(422, 'options is a required, non empty list strings')

        # Original order only maintained in python 3.6+ https://stackoverflow.com/a/7961425
        deduped_options = json.dumps(list(dict.fromkeys(options)))

        if type(request.data.get('question')) != str:
            abort(422, 'question is a required string')

        inserted = query_one('INSERT INTO question (question, options) VALUES (%s, %s) RETURNING id, question, options',
                             (request.data['question'], deduped_options))
        return inserted, status.HTTP_201_CREATED

    return query('SELECT id, question, options FROM question WHERE archived = FALSE;')


@app.route('/api/questions/<int:qid>', methods=['GET', 'DELETE'])
def question_detail(qid):
    if request.method == 'DELETE':
        execute('UPDATE question SET archived = TRUE WHERE id = %s;', (qid,))
        return '', status.HTTP_204_NO_CONTENT

    detail = query_one('SELECT id, question, options FROM question WHERE id = %s;', (qid,))
    return detail if detail else abort(404, 'Question not found')


@app.route('/api/questions/random', methods=['GET'])
def rand_question():
    q = query_one('SELECT id, question, options FROM question WHERE archived = FALSE ORDER BY random() LIMIT 1;')
    return q if q else abort(404, 'No questions exist')


@app.route('/api/questions/<int:qid>/votes', methods=['GET'])
def votes_counts(qid):
    qd = question_detail(qid)
    counts = query('SELECT option_idx, votes FROM vote WHERE question_id = %s', (qid,))
    opt_idx_to_count = {c['option_idx']: c['votes'] for c in counts}
    return {o: opt_idx_to_count.get(i, 0) for i, o in enumerate(qd['options'])}


# Note: GET is unnecessary. It's only present so that the API navigator can attempt a POST via browser UI.
@app.route('/api/questions/<int:qid>/votes/<int:opt_idx>', methods=['GET', 'POST'])
def vote_for_option(qid, opt_idx):
    if not 0 <= opt_idx < len(question_detail(qid)['options']):
        abort(404, 'No such question option. Questions are zero indexed')

    if request.method == 'POST':
        execute('''
        INSERT INTO vote (question_id, option_idx, votes) VALUES (%s, %s, 1) 
        ON CONFLICT (question_id, option_idx) DO UPDATE SET votes = vote.votes + 1;
        ''', (qid, opt_idx))
    return votes_counts(qid)


# Catch all to presumably serve static assets
@app.route('/<path:filename>')
def send_file(filename):
    return send_from_directory(app.static_folder, filename)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
