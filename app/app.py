from flask import Flask, url_for, redirect
app = Flask(__name__)

###########################
# Basic routing
###########################

# Routing to root
@app.route('/')
def hello_world_routing():
    return 'Hello, world!'

#Routing to one name removed from root
@app.route('/foo')
def foo():
    return 'bar!'

# Route anotation does not need to be the
# same path as the anotated function
@app.route('/routeToDifferentName')
def notSameAsPath():
    return 'Yep, routing to a function that has a name different from the routing path name, works.'

# root routes that also lead to other routes must
# end with a '/' or the root route will not work.
@app.route('/mustEndWithSlash/')
@app.route('/mustEndWithSlash/<str>')
def say(str='NO STRING PORVIDED'):
    return '%s' % str

# Routing with variables
@app.route('/sayTwoThings/<str1>/<str2>')
def sayTwoThings(str1, str2):
    return '{}</br>{}'.format(str1, str2)

# url_for() calls a function by name provided as string parameter
# function must have route anotation
fcn_name = 'url_for_helper'
@app.route('/pathCanDifferButParamsMustBeCorrect/<s1>/<s2>')
def url_for_helper(s1, s2):
    return '{}</br>{}'.format(s1, s2)

@app.route('/url_for')
def url_for_test():
    return redirect(url_for(fcn_name, s1='Works', s2='fine'))


###########################
# Jinja2 templating
###########################
from flask import render_template

# render_template() is the flask method that renders jinja2
@app.route('/template/helloWorld/')
@app.route('/template/helloWorld/<name>')
def hello_world_templates(name=None):
    return render_template('hello.html.j2', name=name)


###########################
# HTTP methods
###########################
from flask import request

# By default routes answer to GET. To specify other
# methods use the parameter methods=list-of-methods
@app.route('/HTTP/post', methods=['POST'])
def http_post():
    return 'You succesfully called http_post()!'

# Post variables are accessed with request.form.get('field')
# This method will list form vars, URL params, and header data.
@app.route('/HTTP/postWithVars', methods=['POST'])
def post_with_vars():
    # List form vars (how POST usually sends data)
    ret = "<strong>Form variables:</strong>"
    for key, val in request.form.to_dict().items():
        ret += '</br>{} : {}'.format(key, val)
    # List all header entries
    ret += "</br><strong>Header:</strong>"
    for key, val in request.headers.items():
        ret += '</br>{} : {}'.format(key, val)
    # List URL params (how GET usually sends data)
    ret += "</br><strong>URL parameters:</strong>"
    for key, val in request.args.to_dict().items():
        ret += '</br>{} : {}'.format(key, val)
    return ret