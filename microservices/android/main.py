import requests
from flask import Flask
from flask import request
from lib.tracing import init_tracer
from opentracing.ext import tags
from opentracing.propagation import Format
from random import randint

app = Flask(__name__)
tracer = init_tracer('android')


def http_get(url, param, value):
    span = tracer.active_span
    span.set_tag(tags.HTTP_METHOD, 'GET')
    span.set_tag(tags.HTTP_URL, url)
    span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_CLIENT)
    headers = {}
    tracer.inject(span, Format.HTTP_HEADERS, headers)

    r = requests.get(url,
                     params={param: value},
                     headers=headers,
                     timeout=1)

    assert r.status_code == 200
    return r.text


@app.route("/")
def format():
    service = 'android'
    span_ctx = tracer.extract(Format.HTTP_HEADERS, request.headers)
    span_tags = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER}
    with tracer.start_active_span('request', child_of=span_ctx,
                                  tags=span_tags) as scope:

        hello_to = request.args.get('helloTo')
        scope.span.log_kv(
            {'event': '{} recieves request'.format(service), 'helloTo': hello_to})
        hello_to = '{},{}'.format(hello_to, service)

        try:

            port = 5000
            path = ''
            if randint(1, 2) == 2:
                url = 'http://app-search:%s/%s' % (port, path)
            else:
                url = 'http://app-model:%s/%s' % (port, path)

            hello_str = http_get(url, 'helloTo', hello_to)
            scope.span.log_kv(
                {'event': '{} sends request'.format(service), 'value': 'line 35'})

        except:
            scope.span.log_kv(
                {'event': '{} fails to send request'.format(service), 'value': 'line 35'})
            hello_str = hello_to

        return hello_str


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
