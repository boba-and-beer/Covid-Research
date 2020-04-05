from flask import (Flask, 
      send_from_directory, 
      jsonify, 
      request)
import os
os.environ["JAVA_HOME"] = "/usr/lib/jvm/jdk-11.0.2"
#from server2 import searchDatabase, pysearch, keywords, model

app = Flask(__name__,static_folder='frontend') 

@app.route('/api/search') 
def hello_world():
  #text = request.args.get('text')
  return jsonify([{"Source":"somesource","Text":"sometext","Confidence":"someconfidence"}])
  """)
  try:
      data = searchDatabase(question='these differences reside in the molecular strucure of spike proteins and some other factors. Which receptor combination(s) will cause maximum harm', pysearch=pysearch,
              keywords=keywords, lucene_database='lucene-index-covid-2020-03-27/', BERTSQuAD_Model=model)
      print(data)
      return jsonify(data)
 iexcept Exception as e: 
      print(e)
"""
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
  if path != "" and os.path.exists(app.static_folder + '/' + path):
      return send_from_directory(app.static_folder, path)
  else:
      return send_from_directory(app.static_folder, 'index.html') 

if __name__ == "__main__": 
    app.run(host='0.0.0.0',debug=True) 
