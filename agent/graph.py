from langgraph.graph import END, START, StateGraph

from .nodes import (
    planner,
    researcher,
    critic,
    reporting
)

from .router import (
    decision,
    route_after_decision
)

from .state import ResearchState


def build_graph():

    graph = StateGraph(
        ResearchState
    )

    # Nodes
    graph.add_node(
        "planner",
        planner
    )

    graph.add_node(
        "researcher",
        researcher
    )

    graph.add_node(
        "critic",
        critic
    )

    graph.add_node(
        "decision",
        decision
    )

    graph.add_node(
        "reporting",
        reporting
    )

    # Start
    graph.add_edge(
        START,
        "planner"
    )

    # Normal flow
    graph.add_edge(
        "planner",
        "researcher"
    )

    graph.add_edge(
        "researcher",
        "critic"
    )

    graph.add_edge(
        "critic",
        "decision"
    )

    # Conditional retry / approval
    graph.add_conditional_edges(
        "decision",
        route_after_decision,
        {
            "planner": "planner",
            "reporting": "reporting"
        }
    )

    # Finish
    graph.add_edge(
        "reporting",
        END
    )

    return graph.compile()


app = build_graph()