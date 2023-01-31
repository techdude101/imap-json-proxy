from flask import make_response, jsonify

def generate_unauthorized():
  message = jsonify(message='Unauthorized')
  return make_response(message, 401)

def generate_created(data):
  message = jsonify(message='Created')
  return make_response(message, 201)

def generate_bad_request(text):
  message = jsonify(message=text)
  return make_response(message, 400)