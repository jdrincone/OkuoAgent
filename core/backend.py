from langchain_core.messages import HumanMessage
from typing import List
from dataclasses import dataclass
from langgraph.graph import StateGraph
from core.graph.state import AgentState
from core.graph.nodes import call_model, call_tools, route_to_tools
from core.data_models import InputData
from config import config
from utils.logger import logger
import uuid
import time

class PythonChatbot:
    def __init__(self, session_id: str = None):
        super().__init__()
        self.session_id = session_id or str(uuid.uuid4())
        self.session_start_time = time.time()
        self.reset_chat()
        self.graph = self.create_graph()
        logger.info(f"Initialized PythonChatbot for session: {self.session_id}")
        
    def create_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node('agent', call_model)
        workflow.add_node('tools', call_tools)

        workflow.add_conditional_edges('agent', route_to_tools)

        workflow.add_edge('tools', 'agent')
        workflow.set_entry_point('agent')
        return workflow.compile()
    
    def user_sent_message(self, user_query, input_data: List[InputData]):
        logger.info(f"Session {self.session_id}: Processing user message with {len(input_data)} datasets")
        
        starting_image_paths_set = set(sum(self.output_image_paths.values(), []))
        input_state = {
            "messages": self.chat_history + [HumanMessage(content=user_query)],
            "output_image_paths": list(starting_image_paths_set),
            "input_data": input_data,
        }

        try:
            result = self.graph.invoke(input_state, {"recursion_limit": config.RECURSION_LIMIT})
            self.chat_history = result["messages"]
            new_image_paths = set(result["output_image_paths"]) - starting_image_paths_set
            self.output_image_paths[len(self.chat_history) - 1] = list(new_image_paths)
            if "intermediate_outputs" in result:
                self.intermediate_outputs.extend(result["intermediate_outputs"])
            
            logger.info(f"Session {self.session_id}: Successfully processed message. Chat history: {len(self.chat_history)} messages")
            
        except Exception as e:
            logger.error(f"Session {self.session_id}: Error processing message: {str(e)}")
            raise

    def reset_chat(self):
        """Reset the chat state for this session."""
        self.chat_history = []
        self.intermediate_outputs = []
        self.output_image_paths = {}
        logger.info(f"Session {self.session_id}: Chat state reset")

    def get_session_info(self) -> dict:
        """Get information about this session."""
        return {
            'session_id': self.session_id,
            'session_age_seconds': time.time() - self.session_start_time,
            'chat_history_length': len(self.chat_history),
            'intermediate_outputs_count': len(self.intermediate_outputs),
            'output_images_count': len(self.output_image_paths)
        }

    def cleanup_session(self):
        """Clean up session resources."""
        logger.info(f"Session {self.session_id}: Cleaning up session resources")
        self.reset_chat()
        # Additional cleanup could be added here
