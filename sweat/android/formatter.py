from flask import Flask
from flask import request
from lib.tracing import init_tracer
from opentracing.ext import tags
from opentracing.propagation import Format
from random import randint

import requests
import time

app = Flask(__name__)
tracer = init_tracer('android')


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
    print("format function in aserv is executing")
    start = time.time()
    span_ctx = tracer.extract(Format.HTTP_HEADERS, request.headers)
    span_tags = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER}
    with tracer.start_active_span('request', child_of=span_ctx, tags=span_tags) as scope:
        hello_to = request.args.get('helloTo')
        scope.span.log_kv({'event': 'android recieves request', 'helloTo': hello_to})

        hello_to = '{},{}'.format(hello_to, 'android')
        scope.span.log_kv({'event': 'android process string', 'hello_to': hello_to})

        try:
            hello_str = http_get(5000, '', 'helloTo', hello_to)
            scope.span.log_kv({'event': 'aserv', 'value': 'line 35'})
        except:
            print("aserv: The get request failed. no further modification to the string")
            hello_str = hello_to

        return hello_str  # two submissions to format servers
        # return hello_to


if __name__ == "__main__":
    print("Running the flask app for android:")
    app.run(debug=True, host='0.0.0.0')
