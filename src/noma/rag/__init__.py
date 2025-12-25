"""RAG (Retrieval Augmented Generation) module."""

from .graphrag import create_graph_instance

__all__ = ["create_graph_instance", "create_ehr_app", "visualize_graph"]


def create_ehr_app(*args, **kwargs):
    from .ehr import create_ehr_app as _create
    return _create(*args, **kwargs)


def visualize_graph(*args, **kwargs):
    from .visualization import visualize_graph as _viz
    return _viz(*args, **kwargs)

