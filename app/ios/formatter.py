import requests
from flask import Flask
from flask import request
from lib.tracing import init_tracer
from opentracing.ext import tags
from opentracing.propagation import Format
from random import randint

import time

app = Flask(__name__)
tracer = init_tracer('ios')


def http_get(port, path, param, value):
    url = 'http://app-model:%s/%s' % (port, path)
    if randint(1, 2) == 2:
        url = 'http://app-search:%s/%s' % (port, path)

    span = tracer.active_span
    span.set_tag(tags.HTTP_METHOD, 'GET')
    span.set_tag(tags.HTTP_URL, url)
    span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_CLIENT)
    headers = {}
    tracer.inject(span, Format.HTTP_HEADERS, headers)

    r = requests.get(url, params={param: value}, headers=headers, timeout=1)
    assert r.status_code == 200
    return r.text


@app.route("/format")
def format():
    span_ctx = tracer.extract(Format.HTTP_HEADERS, request.headers)
    span_tags = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER}
    with tracer.start_active_span('request', child_of=span_ctx, tags=span_tags) as scope:
        hello_to = request.args.get('helloTo')
        scope.span.log_kv({'event': 'ios recieves request', 'helloTo': hello_to})

        hello_to = hello_to + ',ios'
        try:
            hello_str = http_get(5000, 'format', 'helloTo', hello_to)
            scope.span.log_kv({'event': 'ios', 'value': 'line 35'})
        except:
            print("ios: The get request failed. no further modification to the string")
            hello_str = hello_to

        return hello_str  # two submissions to format servers


if __name__ == "__main__":
    print("Running the flask app for ios:")
    bug = False
    app.run(debug=True, host='0.0.0.0')
