from flask import Flask
from flask import request
from lib.tracing import init_tracer
from time import sleep
from opentracing.ext import tags
from opentracing.propagation import Format
from random import randint

app = Flask(__name__)
tracer = init_tracer('db')


@app.route("/")
def format():
    span_ctx = tracer.extract(Format.HTTP_HEADERS, request.headers)
    span_tags = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER}
    with tracer.start_active_span('end-chain', child_of=span_ctx, tags=span_tags) as scope:
        hello_to = request.args.get('helloTo')
        bug = request.args.get('bug')
        if bug == "True":
            bug = True
        elif bug == "False":
            bug = False
        scope.span.log_kv({'event': 'db read bug', 'bug status': str(bug), 'bug taIp': str(type(bug))})
        if bug:
            scope.span.log_kv({'event': 'db-bug true', 'bug status': str(bug)})
            sleep(.1)
        else:
            scope.span.log_kv({'event': 'db-bug false', 'bug status': str(bug)})

        return hello_to + ',db'


if __name__ == "__main__":
    # app.run(port=8081)
    app.run(debug=True, host='0.0.0.0')
