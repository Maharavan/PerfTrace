from .sqlite_storage import ProfilerLiteDB
from flatten_json import flatten
def get_storage(backend='sqlite', report=dict):
    """Factory function to get storage backend"""
    if backend == 'sqlite':
        report = standardize_metrics_format(report)
        return ProfilerLiteDB(report)



def standardize_metrics_format(report):

    report_flatten = flatten(report)
    print(report_flatten)
    return report_flatten