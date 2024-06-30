from flask import Flask, request, jsonify
from flask_cors import CORS
from opt import optimize
app = Flask(__name__)
CORS(app)  # Enable CORS for all origins

@app.route('/process-info', methods=['POST'])
def process_info():
    data = request.json
    draft_id = data.get('draft_id')
    
    # Call your Python function with the provided parameters
    result = optimize(draft_id)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
