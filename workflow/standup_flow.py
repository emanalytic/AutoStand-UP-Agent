from langgraph.graph import StateGraph
from agents.github_fetcher import github_fetcher_node
from typing import TypedDict, List

class StandupState(TypedDict):
    owner: str
    repo: str
    hours: int
    github_activity: List[dict]  # will store fetched commit/PR data

def build_standup_flow():
    graph = StateGraph(StandupState)

    graph.add_node("Fetch GitHub", github_fetcher_node)
    # graph.add_node("Fetch Notion", fetch_notion_updates)
    # graph.add_node("Aggregate", aggregate_activities)
    # graph.add_node("Format", format_standup_message)
    # graph.add_node("Post", post_to_slack)

    # Define the flow
    graph.set_entry_point("Fetch GitHub")
    # graph.add_edge("Fetch GitHub", "Fetch Notion")
    # graph.add_edge("Fetch Notion", "Aggregate")
    # graph.add_edge("Aggregate", "Format")
    # graph.add_edge("Format", "Post")

    return graph.compile()

def main():
    graph = build_standup_flow()  # build your workflow

    # Inputs for GitHub Fetcher
    state = {
        "owner": "emanalytic",
        "repo": "AutoStand-UP-Agent",
        "hours": 84
    }

    # Run the workflow
    result = graph.invoke(state)  # Pass the input state here
    print("✅ Workflow Result:", result)

if __name__ == "__main__":
    main()