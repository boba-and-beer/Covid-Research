from flask import (Flask, 
      send_from_directory, 
      jsonify, 
      request)
import os
os.environ["JAVA_HOME"] = "/usr/lib/jvm/jdk-11.0.2"
from test_model import searchDatabase, pysearch, KEYWORDS, model

app = Flask(__name__,static_folder='frontend')

# Should the following include the methods='post' argumetn?
def predict(text):
  """Returns a dictionary item.
  """
  data = searchDatabase(question=text)
  print(data)
  # If there are no predictions return uncertainty.
  if len(data) == 0:
    return [
        {"Source":"Unconfident About Any result","Text":"Unconfident About Any result","Confidence":0}
    ]
  else:
    return data

@app.route('/api/search') 
def hello_world():
  """Returns prediction for questions.
  """
  text = request.args.get('text')
  return jsonify(predict(text))

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
  if path != "" and os.path.exists(app.static_folder + '/' + path):
      return send_from_directory(app.static_folder, path)
  else:
      return send_from_directory(app.static_folder, 'index.html')

if __name__ == "__main__": 
    app.run(host='0.0.0.0',debug=True) 
