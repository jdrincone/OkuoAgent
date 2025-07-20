from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from .state import AgentState
import json
from typing import Literal
from .tools import complete_python_task
from langgraph.prebuilt import ToolInvocation, ToolExecutor
import os
from config import config
from utils.logger import logger


llm = ChatOpenAI(
    model=config.OPENAI_MODEL, 
    temperature=config.OPENAI_TEMPERATURE
)

tools = [complete_python_task]

model = llm.bind_tools(tools)
tool_executor = ToolExecutor(tools)

with open(os.path.join(os.path.dirname(__file__), "../prompts/main_prompt.md"), "r") as file:
    prompt = file.read()

chat_template = ChatPromptTemplate.from_messages([
    ("system", prompt),
    ("placeholder", "{messages}"),
])
model = chat_template | model

def create_data_summary(state: AgentState) -> str:
    summary = ""
    variables = []
    for d in state["input_data"]:
        variables.append(d.variable_name)
        summary += f"\n\nVariable: {d.variable_name}\n"
        summary += f"Description: {d.data_description}"
    
    if "current_variables" in state:
        remaining_variables = [v for v in state["current_variables"] if v not in variables]
        for v in remaining_variables:
            summary += f"\n\nVariable: {v}"
    return summary

def route_to_tools(
    state: AgentState,
) -> Literal["tools", "__end__"]:
    """
    Use in the conditional_edge to route to the ToolNode if the last message
    has tool calls. Otherwise, route back to the agent.
    """

    if messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    
    # Check if the last message has tool calls
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        logger.info(f"Routing to tools: {len(ai_message.tool_calls)} tool calls detected")
        return "tools"
    
    # Check if we have a meaningful response without tool calls
    if hasattr(ai_message, "content") and ai_message.content:
        content = ai_message.content.strip()
        # If the AI provided a meaningful response without tool calls, end the conversation
        if len(content) > 10:  # Minimum meaningful response length
            logger.info("Routing to end: AI provided meaningful response without tool calls")
            return "__end__"
    
    # If we have too many messages, end to prevent infinite loops
    message_count = len(messages)
    if message_count > 10:  # Prevent excessive back-and-forth
        logger.warning(f"Too many messages ({message_count}), ending conversation to prevent infinite loop")
        return "__end__"
    
    # Default: continue to tools if we have tool calls, otherwise end
    logger.info("Routing to end: No tool calls and no meaningful response")
    return "__end__"

def call_model(state: AgentState):
    current_data_template  = """The following data is available:\n{data_summary}"""
    current_data_message = HumanMessage(content=current_data_template.format(data_summary=create_data_summary(state)))
    state["messages"] = [current_data_message] + state["messages"]

    try:
        llm_outputs = model.invoke(state)
        logger.info(f"Model invoked successfully, response length: {len(str(llm_outputs))}")
        return {"messages": [llm_outputs], "intermediate_outputs": [current_data_message.content]}
    except Exception as e:
        logger.error(f"Error in call_model: {str(e)}")
        # Return a fallback response to prevent infinite loops
        fallback_message = AIMessage(content="I encountered an error processing your request. Please try rephrasing your question.")
        return {"messages": [fallback_message], "intermediate_outputs": [f"Error: {str(e)}"]}

def call_tools(state: AgentState):
    last_message = state["messages"][-1]
    tool_invocations = []
    
    if isinstance(last_message, AIMessage) and hasattr(last_message, 'tool_calls'):
        tool_invocations = [
            ToolInvocation(
                tool=tool_call["name"],
                tool_input={**tool_call["args"], "graph_state": state}
            ) for tool_call in last_message.tool_calls
        ]

    if not tool_invocations:
        logger.warning("No tool invocations found in call_tools")
        return {"messages": []}

    try:
        responses = tool_executor.batch(tool_invocations, return_exceptions=True)
        tool_messages = []
        state_updates = {}

        for tc, response in zip(last_message.tool_calls, responses):
            if isinstance(response, Exception):
                logger.error(f"Tool execution error: {str(response)}")
                # Create error message instead of raising
                tool_messages.append(ToolMessage(
                    content=f"Error executing tool: {str(response)}",
                    name=tc["name"],
                    tool_call_id=tc["id"]
                ))
            else:
                message, updates = response
                tool_messages.append(ToolMessage(
                    content=str(message),
                    name=tc["name"],
                    tool_call_id=tc["id"]
                ))
                state_updates.update(updates)

        if 'messages' not in state_updates:
            state_updates["messages"] = []

        state_updates["messages"] = tool_messages 
        logger.info(f"Tools executed successfully: {len(tool_messages)} tool messages")
        return state_updates
        
    except Exception as e:
        logger.error(f"Error in call_tools: {str(e)}")
        # Return error message instead of raising
        error_message = ToolMessage(
            content=f"Error executing tools: {str(e)}",
            name="error",
            tool_call_id="error"
        )
        return {"messages": [error_message]}

