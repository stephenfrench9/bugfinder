import datetime
from elasticsearch import Elasticsearch
from flask import Flask

app = Flask(__name__)

# Hard-coded Bugfinder parameters.
# How many traces in the past does Bugfinder analyze?
TRACE_WINDOW = 1000  # traces
# What is the definition of a slow response?
THRESHOLD = 60000  # milliseconds


def power_set(seq):
    """
    Returns all the subsets of this set. This is a generator.
    """
    if len(seq) <= 1:
        yield seq
        yield []
    else:
        for item in power_set(seq[1:]):
            yield [seq[0]] + item
            yield item


@app.route("/format")
def conditional_distributions():


    es = Elasticsearch([{'host': 'elasticsearch', 'port': 9200}])

    d = str(datetime.datetime.utcnow()).split()[0]
    # get list of all traces
    res = es.search(index='jaeger-span-' + d, size=TRACE_WINDOW)

    all_traces = res['hits']['hits']
    app.logger.debug("all_traces: %s" % type(all_traces))
    app.logger.debug("all_traces: %s" % len(all_traces))
    app.logger.debug("all_traces[0]: %s" % type(all_traces[0]))


    # Break lists of traces into lists of services, trace_ids, and spans_ids.
    services = []
    traces = []
    spans = []
    for trace in all_traces:
        service = trace['_source']['process']['serviceName']
        trace_id = trace['_source']['traceID']
        span_id = trace['_source']['spanID']
        if service not in services:
            services.append(service)
        if trace_id not in traces:
            traces.append(trace_id)
        if span_id not in spans:
            spans.append(span_id)

    # Build events dictionary. Given a trace_id and a service, the 'events'
    # dictionary will tell you the duration of that service call.
    events = {}
    for i in range(len(traces)):
        search = {"query": {"match": {'traceID': traces[i]}}}
        res = es.search(index='jaeger-span-' + d, body=search,
                        size=TRACE_WINDOW)
        all_traces = res['hits']['hits']  # all the spans to do with this trace

        for trace in all_traces:
            service = trace['_source']['process']['serviceName']
            trace_id = trace['_source']['traceID']
            # span_id = trace['_source']['spanID']
            duration = trace['_source']['duration']
            if trace_id not in events.keys():
                events[trace_id] = {}
            events[trace_id][service] = duration

    # Identify slow traces.
    for trace in events.keys():
        slow = False
        for service in events[trace].keys():
            if events[trace][service] > THRESHOLD:
                slow = True
        events[trace]['slow'] = slow

    # Get counts for (path, speed).
    slow_counts = {}
    fast_counts = {}
    for trace in traces:
        # Find all the marginal arguments for ONE trace.
        traces_in_span = []
        # traces = list(events.keys())
        for key in events[trace].keys():
            if key != 'slow':
                traces_in_span.append(key)

        traces_in_span = sorted(traces_in_span)

        # Generate all combinations of services for which you want
        # performance metrics.
        power_sets = power_set(traces_in_span)
        marginals_args = []
        marginal_arg_set = "initialized"
        while marginal_arg_set != "done":
            marginal_arg_set = next(power_sets, 'done')
            if marginal_arg_set != [] and marginal_arg_set != 'done':
                marginals_args.append(marginal_arg_set)

        # Add all the marginal_args to the distribution.
        for args in marginals_args:
            if events[trace]['slow']:
                if ",".join(args) not in list(slow_counts.keys()):
                    slow_counts[",".join(args)] = 1
                else:
                    slow_counts[",".join(args)] += 1
            elif not events[trace]['slow']:
                if ",".join(args) not in list(fast_counts.keys()):
                    fast_counts[",".join(args)] = 1
                else:
                    fast_counts[",".join(args)] += 1

    # Calculate the conditional distributions.
    cond_dist = {}
    for slow_args, slow_count in slow_counts.items():
        if slow_args in list(fast_counts.keys()):
            cond_dist[slow_args] = slow_count / \
                                   (slow_count + fast_counts[slow_args])
        else:
            cond_dist[slow_args] = slow_count / slow_count

    # Reformat conditional distributions to look like
    # [[service1, service2, .98], ..] etc.
    keys = []
    for k, v in cond_dist.items():
        keys.append(k.split(','))
        keys[-1].append(v)

    # Place single services at the front of the list, and larger combinations
    # of services at the end.
    diagnosis = sorted(keys, key=len)

    # Build the final result string to be returned.
    result = ""
    for diagnosis in diagnosis:
        services = ' & '.join(diagnosis[:-1])
        result = result + \
                 "P(" + str(services) + ") = " + \
                 str(round(diagnosis[-1], 2)) + \
                 "<br/>"
    app.logger.debug(result[0:120])
    return "that day"
    return '<font size="22">' + result + '</font>'


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
