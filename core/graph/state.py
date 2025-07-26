import operator
from typing import Sequence, TypedDict, Annotated, Dict, List
from langchain_core.messages import BaseMessage
import pandas as pd


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    dataframes: Dict[str, pd.DataFrame]
    intermediate_outputs: Annotated[List[dict], operator.add]
    current_variables: dict
    output_image_paths: Annotated[List[str], operator.add]

