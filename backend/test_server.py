from flask import Flask, send_file


frontData = None
backData = None


def loadData():
    pass


api = Flask(__name__)

@api.route('/profile')
def my_profile():
    response_body = {
        "name": "Nagato",
        "about" :"Hello! I'm a full stack developer that loves python and javascript"
    }

    return response_body


@api.route('/get_ib_front')
def getIbFront():
    return send_file("ibFrontend.json")


@api.route('/get_ib_back')
def getIbBack():
    return send_file("ibBackend.json")


@api.route('/constructor/test', methods=['GET', 'POST'])
def make_program():
    pass


api.run()