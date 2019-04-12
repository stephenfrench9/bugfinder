import requests
from flask import Flask
from flask import request
from lib.tracing import init_tracer
from opentracing.ext import tags
from opentracing.propagation import Format

from time import sleep

app = Flask(__name__)
tracer = init_tracer('model')


def http_get(port, path, param, value, bug):
    url = 'http://app-db:%s/%s' % (port, path)

    span = tracer.active_span
    span.set_tag(tags.HTTP_METHOD, 'GET')
    span.set_tag(tags.HTTP_URL, url)
    span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_CLIENT)
    headers = {}
    tracer.inject(span, Format.HTTP_HEADERS, headers)

    r = requests.get(url, params={param: value, 'bug': bug}, headers=headers, timeout=1)
    assert r.status_code == 200
    return r.text


@app.route("/format")
def format():
    span_ctx = tracer.extract(Format.HTTP_HEADERS, request.headers)
    span_tags = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER}
    with tracer.start_active_span('request', child_of=span_ctx, tags=span_tags) as scope:
        scope.span.log_kv({'event': 'model-server', 'value': 'line 32'})
        hello_to = request.args.get('helloTo')
        hello_to = hello_to + ', model'
        bug = request.args.get('bug')
        scope.span.log_kv({'event': 'model-got bug', 'value': bug})
        scope.span.log_kv({'event': 'model-got bug', 'value': str(type(bug))})

        try:
            scope.span.log_kv({'event': 'model-server', 'value': 'trying get'})
            hello_str = http_get(5000, 'format', 'helloTo', hello_to, bug)
            scope.span.log_kv({'event': 'model-server', 'value': 'get success'})
        except:
            hello_str = hello_to

        return hello_str  # two submissions to format servers


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
