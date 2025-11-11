from langchain.agents import create_agent

from src.agents.prompts.internal_agent_prompt import get_prompt_internal_agent
from src.agents.tools.tools import search_internal_qa_tool, summarize_issues_tool
from src.models.langchain_model_loader import LangchainModelLoader

loader = LangchainModelLoader()

openai_basic_model = loader.init_model_openai_basic()

prompt_internal_agent = get_prompt_internal_agent()

internal_agent = create_agent(
    openai_basic_model,
    tools=[search_internal_qa_tool, summarize_issues_tool],
    system_prompt=prompt_internal_agent,
)
