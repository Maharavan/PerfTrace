from flatten_json import flatten

def standardize_metrics_format(report):

    report_flatten = flatten(report)
    print(report_flatten)
    return report_flatten