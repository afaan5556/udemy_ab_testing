# From the course: Bayesin Machine Learning in Python: A/B Testing
# https://deeplearningcourses.com/c/bayesian-machine-learning-in-python-ab-testing
# https://www.udemy.com/bayesian-machine-learning-in-python-ab-testing
from __future__ import print_function, division
from builtins import range
# Note: you may need to update your version of future
# sudo pip install -U future


import numpy as np
from flask import Flask, jsonify, request
from scipy.stats import beta
import random

EPS = 0.1

# create an app
app = Flask(__name__)


# define bandits
# there's no "pull arm" here
# since that's technically now the user/client
class Bandit:
  def __init__(self, name):
    self.clicks = 0
    self.views = 0 # Views is N in this context
    self.p_estimate = 0 # Initialize to zero as before
    self.name = name

  def add_view(self):
    self.views += 1
    # View endpoint used each time ad is shown
    # So updating with a 0 instead of self.pull() (previously x) here
    self.p_estimate = ((self.views - 1)*self.p_estimate) / self.views

  def add_click(self):
    self.clicks += 1
    # Click endpoint only used by client when action == 1
    # So updating with a +1 instead of self.pull() (previously x) here
    self.p_estimate = ((self.views - 1)*self.p_estimate + 1) / self.views

    # print some helpful stats
    if self.views % 50 == 0:
      print("%s: clks=%s, views=%s" % (self.name, self.clicks, self.views))
  
# initialize bandits
banditA = Bandit('A')
banditB = Bandit('B')

@app.route('/get_ad')
def get_ad():
  if np.random.random() < EPS:
    # Explore - choose bandit randomly
    bandit = random.choice([banditA, banditB])
    ad = bandit.name
    bandit.add_view()
  elif banditA.p_estimate > banditB.p_estimate:
    # Exploit A
    ad = 'A'
    banditA.add_view()
  elif banditA.p_estimate < banditB.p_estimate:
    # Exploit B
    ad = 'B'
    banditB.add_view()
  else:
    # Initial condition when p_estimate = 0 for banditA and banditB
    # Or also if at a later step banditA.p_estimate == banditA.p_estimate by chance
    # Choose bandit randomly
    bandit = random.choice([banditA, banditB])
    ad = bandit.name
    bandit.add_view()

  return jsonify({'advertisement_id': ad})

@app.route('/click_ad', methods=['POST'])
def click_ad():
  result = 'OK'
  if request.form['advertisement_id'] == 'A':
    banditA.add_click()
    pass
  elif request.form['advertisement_id'] == 'B':
    banditB.add_click()
    pass
  else:
    result = 'Invalid Input.'

  # nothing to return really
  return jsonify({'result': result})

if __name__ == '__main__':
  app.run(host='127.0.0.1', port='8888')