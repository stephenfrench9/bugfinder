import requests
from flask import Flask
from flask import request
from lib.tracing import init_tracer
from opentracing.ext import tags
from opentracing.propagation import Format
from random import randint

app = Flask(__name__)
tracer = init_tracer('search')


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

    r = requests.get(url, params={param: value, 'bug': bug}, headers=headers,
                     timeout=1)
    assert r.status_code == 200
    return r.text


@app.route("/")
def format():
    # Get information about the span that is parent to this request.
    # Pull the information stored by Jaeger in the request headers.
    span_ctx = tracer.extract(Format.HTTP_HEADERS, request.headers)
    span_tags = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER}

    # Generate a new span. This new span is the child of the span that
    # made this request.
    with tracer.start_active_span('request', child_of=span_ctx,
                                  tags=span_tags) as scope:
        # Pull the application's information from the request header.
        # Add the name of this micro-service to the list of micro-services
        # in this trace.
        hello_to = request.args.get('helloTo')
        hello_to = hello_to + ',search'
        try:
            bug = True
            # Call the next micro-service, Adding the next micro-service to
            # the list of micro-services involved in fulfilling this
            # request
            hello_str = http_get(5000, '', 'helloTo', hello_to, bug)
            # Log with Jaeger's logging framework
            scope.span.log_kv({'event': 'search get request successful'})
        except:
            hello_str = hello_to

        return hello_str  # two submissions to format servers


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
