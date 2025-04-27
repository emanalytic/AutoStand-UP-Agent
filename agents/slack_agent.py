import os
from slack_sdk import WebClient
from langgraph.graph import StateGraph
from typing import TypedDict, List, Dict
import requests
from groq import Groq


# Load credentials
SLACK_BOT_TOKEN = "xoxb-8798470229634-8786752600358-4TZot2fze0cEuzIAHZ7IpzV9"
SLACK_CHANNEL   = "#daily-standup"
GROQ_API_KEY    = "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"
LLM_MODEL       = "llama-3.3-70b-versatile"


# Initialize clients
slack_client = WebClient(token=SLACK_BOT_TOKEN)
groq_client = Groq(api_key=GROQ_API_KEY)

def llm_format_node(state: Dict) -> Dict:
    report = state.get("standup_report", {})
    # Build chat message
    messages = [
        {"role": "system", "content": "You are an assistant that formats a daily stand-up report for Slack. I want you to use slack writing style to bold, points and other formatting"},
        {"role": "user",  "content": (
            "Input is a JSON object mapping usernames to sections: done_yesterday, in_progress, blockers.\n"
            f"Report JSON: {report}\n"
            "Produce a Slack markdown message with headings, bullet points, and clear sections."
        )}
    ]
    # Call Groq chat completion
    completion = groq_client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )
    content = completion.choices[0].message.content
    state["slack_text"] = content
    return state

def slack_post_node(state: Dict) -> Dict:
    text = state.get("slack_text", "")
    slack_client.chat_postMessage(channel=SLACK_CHANNEL, text=text)
    return state

# LangGraph state & flow definitions
tf = TypedDict
class SlackLLMState(TypedDict, total=False):
    standup_report: Dict[str, Dict[str, List[Dict]]]
    slack_text: str

# Build graph
graph = StateGraph(SlackLLMState)
graph.add_node("llm_format", llm_format_node)
graph.add_node("slack_post", slack_post_node)
graph.set_entry_point("llm_format")
graph.add_edge("llm_format", "slack_post")
graph.set_finish_point("slack_post")

slack_app = graph.compile()

if __name__ == "__main__":
    # jUST FOR NOW WILL BE pass in standup_report from aggregator
    dummy = {
        "Maryam": {"done_yesterday": [{"message": "Fixed bug #42"}],
                  "in_progress": [{"Task Name": "Feature X", "Due Date": "2025-05-01"}],
                  "blockers": []}
    }
    slack_app.invoke({"standup_report": dummy})  
