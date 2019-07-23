import requests

from flask import Flask
from flask import request
from lib.tracing import init_tracer
from opentracing.ext import tags
from opentracing.propagation import Format
from random import randint

app = Flask(__name__)
tracer = init_tracer('search')
bug = True


def http_get(port, path, param, value, bug):
    url = 'http://app-db:%s/%s' % (port, path)
    if not randint(1, 3) == 2:
        url = 'http://app-db2:%s/%s' % (port, path)

    span = tracer.active_span
    span.set_tag(tags.HTTP_METHOD, 'GET')
    span.set_tag(tags.HTTP_URL, url)
    span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_CLIENT)
    headers = {}
    tracer.inject(span, Format.HTTP_HEADERS, headers)

    r = requests.get(url, params={param: value, 'bug': bug}, headers=headers, timeout=1)
    assert r.status_code == 200
    return r.text


@app.route("/")
def format():
    global bug
    span_ctx = tracer.extract(Format.HTTP_HEADERS, request.headers)
    span_tags = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER}
    with tracer.start_active_span('request', child_of=span_ctx, tags=span_tags) as scope:
        hello_to = request.args.get('helloTo')
        hello_to = hello_to + ',search'
        # if randint(1,20) == 4:
        # bug = True
        try:
            hello_str = http_get(5000, '', 'helloTo', hello_to, bug)
            scope.span.log_kv({'event': 'search get request successful'})
        except:
            hello_str = hello_to

        hello_str = hello_str
        return hello_str  # two submissions to format servers


if __name__ == "__main__":
    print("Running the flask app for search:")
    app.run(debug=True, host='0.0.0.0')
