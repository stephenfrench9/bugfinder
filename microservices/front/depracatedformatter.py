import time
import requests
from flask import Flask
from flask import request
from random import randint

app = Flask(__name__)


def http_get(rooturl, port, path, param, value):
    url = rooturl % (port, path)
    # r = requests.get(url, params={param: value}, timeout=1)
    session = requests.Session()
    session.trust_env = False
    r = session.get(url, params={param: value}, timeout=1)
    assert r.status_code == 200
    return r.text


@app.route("/format")
def format():
    grand_result = ""

    rooturl = 'http://app-ios:%s/%s'
    try:
        warmup = http_get(rooturl, 5000, 'format', 'helloTo', hello_to)
    except:
        warmup = "(the warmup get failed)"

    for n in range(40):

        q = randint(1, 2)

        if q == 1:
            hello_to = "Jeff"
            start = time.time()
            try:
                android_url = 'http://app-android:%s/%s'
                android_response = http_get(android_url, 5000, 'format', 'helloTo', hello_to)
            except:
                android_response = hello_to + ",failed request"
            android_response = android_response.split(",")
            end = time.time()
            duration = round(end - start, 3)*1000
            response = android_response[1] + " : " + str(duration) + " ms" # Keep response
            # response = "user measures: " + str(duration) + " ms" # Discard microservice results

        elif q == 2:
            hello_to = "Eric"
            start = time.time()
            try:
                start = time.time()
                web_url = 'http://app-ios:%s/%s'
                web_response = http_get(web_url, 5000, 'format', 'helloTo', hello_to)
            except:
                web_response = hello_to + ",failed request"
            web_response = web_response.split(",")
            end = time.time()
            duration = round(end - start, 3)*1000
            response = web_response[1] + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + " : " + str(duration) + " ms" # Keep response

            # response = "user measures: " + str(duration) + " ms" # Discard service response

        grand_result = grand_result + response + "<br/>"

        # grand_result = grand_result + \
        #                android_response + "<br/>" + \
        #                web_response + "<br/>" + \
        #                api_response + "<br/>" + \
        #                ios_response + "<br/>"

    grand_result = '<font size="22">' + grand_result + '</font>'

    return grand_result


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
