from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

system = """You are a question re-writer that converts an input question into a highly optimized version for web search. \n
Analyze the input, understand the underlying semantic intent, and output just the rewritten query string."""

re_write_prompt = ChatPromptTemplate.from_messages([
    ("system", system),
    ("human", "Here is the initial question: \n\n {question} \n\n Formulate an improved web search query."),
])

# LCEL Rewriter Chain
rewriter_chain = re_write_prompt | llm | StrOutputParser()