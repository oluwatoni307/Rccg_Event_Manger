from langchain_community.tools import TavilySearchResults
import os

os.environ["TAVILY_API_KEY"] = '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'

tool = TavilySearchResults(
    api_key = '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',
    max_results=6,
    search_depth="advanced",
    include_answer=True,
    include_raw_content=False,
    include_images=True,
    # include_domains=[...],
    # exclude_domains=[...],
    # name="...",            # overwrite default tool name
    # description="...",     # overwrite default tool description
    # args_schema=...,       # overwrite default args_schema: BaseModel
)
# ANSWER =tool.invoke({"query": "youth convention 2024 rccg"})
# print(ANSWER)

from prompt import llm, theme_prompt, url_prompt
from pydant import parser,event






# Define the graph

from langgraph.prebuilt import create_react_agent
from langchain_core.output_parsers import StrOutputParser
import re
import json
graph = create_react_agent(llm, tools=[tool], state_modifier= theme_prompt)
url_finder = create_react_agent(llm, tools=[tool], state_modifier= url_prompt)



def process_agent(query):
    inputs = {"messages": [("user", query)]}
    parser = StrOutputParser()

    answer = graph.invoke(inputs)
    answer = answer["messages"][-1].content
    cleaned_json = re.sub(r'^[^{]*|[^}]*$', '', answer)

    answer_dict = json.loads(cleaned_json)
    return answer_dict['Theme']



def get_url (query):
    inputs = {"messages": [("user", query)]}
    parser = StrOutputParser()

    answer = url_finder.invoke(inputs)
    answer = answer["messages"][-1].content
    cleaned_json = re.sub(r'^[^{]*|[^}]*$', '', answer)

    answer_dict = json.loads(cleaned_json)
    return answer_dict
    

if __name__ == "__main__":
    # answer = process_agent(' theme of YOUTH CONVENTION  2 OCTOBER 2024')
    # print(answer)
    
    answer = get_url(' Holy Ghost september 2024')
    print(answer)