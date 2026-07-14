from graph.state import AgentState
from langgraph.graph import StateGraph, END, START
from graph.nodes import (
    skills_node, 
    education_node, 
    experience_node, 
    orchestrator_node, 
    extract_cv,
    extract_jd,
    check_cv_node,
    check_jd_node,
    should_continue,
    coordinator,
    coordinator_continue
    )

def get_graph():

    workflow = StateGraph(state_schema=AgentState)

    workflow.add_node("extract_jd", extract_jd)
    workflow.add_node("check_cv", check_cv_node)
    workflow.add_node("check_jd", check_jd_node)
    workflow.add_node("coordinator", coordinator)

    workflow.add_node("CV_parser", extract_cv)
    workflow.add_node("Skill_Matcher", skills_node)
    workflow.add_node("Eucation_Scorer", education_node)
    workflow.add_node("Experience_Scorer", experience_node)
    workflow.add_node("Orchestrator", orchestrator_node)

    workflow.add_edge(START,"check_jd")
    workflow.add_conditional_edges(
        "check_jd",
        should_continue,
        {
            "True": "extract_jd",
            "False": END
        }
    )

    workflow.add_edge("extract_jd","coordinator")

    workflow.add_conditional_edges(
        "coordinator",
        coordinator_continue,
        {
            "True": "check_cv",
            "False": END
        }
    )

    workflow.add_conditional_edges(
        "check_cv",
        should_continue,
        {
            "True": "CV_parser",
            "False": "coordinator"
        }
    )
    workflow.add_edge("CV_parser", "Skill_Matcher")
    workflow.add_edge("CV_parser", "Eucation_Scorer")
    workflow.add_edge("CV_parser", "Experience_Scorer")

    workflow.add_edge("Skill_Matcher", "Orchestrator")
    workflow.add_edge("Eucation_Scorer", "Orchestrator")
    workflow.add_edge("Experience_Scorer", "Orchestrator")
    workflow.add_edge("Orchestrator", "coordinator")

    graph = workflow.compile()
    return graph
