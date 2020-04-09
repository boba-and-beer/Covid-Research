"""
Testing suite for app.
"""
from inference import searchDatabase, pysearch, KEYWORDS, model, LUCENE_DATABASE_PATH
import pytest
import os
import time

def test_inference_workes_simple():
    """Test working inference.
    """
    t1 = time.time()
    answer = searchDatabase(question="Where does coronavirus come from?")
    t2 = time.time()
    print("Answer is")
    print(answer)
    print(t2-t1)
    assert answer is not None
    assert len(answer) > 1

def test_lucene_path():
    """Make sure lucene database exists.
    """ 
    assert os.path.exists(LUCENE_DATABASE_PATH), "Lucene database is not at " + LUCENE_DATABASE_PATH