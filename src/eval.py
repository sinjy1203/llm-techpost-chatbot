import os
import json
import datetime
import asyncio
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import pandas as pd
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langfuse import get_client
from langfuse.langchain import CallbackHandler
from workflow import ReactAgent
from workflow.tools import *
from workflow.state import State


load_dotenv(override=True)

langfuse_client = get_client()
langfuse_handler = CallbackHandler()

LLM_MODEL = os.getenv("LLM_MODEL")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
QDRANT_URL = os.getenv("QDRANT_URL")
MAX_EXECUTE_TOOL_COUNT = int(os.getenv("MAX_EXECUTE_TOOL_COUNT"))

EVAL_SYSTEM_TEMPLATE = """
You are a helpful assistant that evaluates the quality of the retrieved context and generated answer. 


<retrieved_context_score_description>
0: When the retrieved context is not relevant to the references in the test data
0.5: When part of the references in the test data is included in the retrieved context
1: When all the references in the test data is included in the retrieved context
</retrieved_context_score_description>

<generated_answer_score_description>
When evaluating the generated_answer, first examine the question and answer from the test data to identify the key elements that must be included.
0: When the generated answer does not include any of the key elements
0.5: When the generated answer includes some of the key elements
1: When the generated answer includes all the key elements
</generated_answer_score_description>
"""

EVAL_USER_TEMPLATE = """
<test_data>
{test_data}
</test_data>

<retrieved_contexts>
{retrieved_contexts}
</retrieved_contexts>

<generated_answer>
{generated_answer}
</generated_answer>
"""

class EvalResult(BaseModel):
    retrieved_context_score_reasoning: str = Field(description="The reasoning of the retrieved context score in Korean")
    retrieved_context_score: float = Field(description="The score of the retrieved context")
    generated_answer_score_reasoning: str = Field(description="The reasoning of the generated answer score in Korean")
    generated_answer_score: float = Field(description="The score of the generated answer")


async def generate_answer(test_data, agent):
    initial_state = State(
        messages=[HumanMessage(content=test_data["question"])],
        execute_tool_count=0
    )
    config = {
        "configurable": {
            "max_execute_tool_count": MAX_EXECUTE_TOOL_COUNT,
            "langfuse_client": langfuse_client
        },
        "callbacks": [langfuse_handler]
    }
    response = await agent.ainvoke(initial_state, config=config)

    return response


async def eval_agent(test_data, agent, eval_chain):
    response = await generate_answer(test_data, agent)

    retrieved_contexts = []
    for message in response["messages"]:
        if message.type == "tool":
            retrieved_contexts.append(message.content)

    retrieved_contexts_str = json.dumps(retrieved_contexts, ensure_ascii=False, indent=2)
    generated_answer = response["messages"][-1].content

    eval_result = await eval_chain.ainvoke(
        {
            "test_data": json.dumps(test_data, ensure_ascii=False, indent=2), 
            "retrieved_contexts": retrieved_contexts_str, 
            "generated_answer": generated_answer
        }
    )

    return retrieved_contexts, generated_answer, eval_result

async def main():
    agent = ReactAgent(
        model_kwargs={
            "model": LLM_MODEL,
            "temperature": LLM_TEMPERATURE
        },
        tools=[
            GeminiSearchTool(
                qdrant_url=QDRANT_URL,
                embedding_model=EMBEDDING_MODEL
            ),
            OpenaiSearchTool(
                qdrant_url=QDRANT_URL,
                embedding_model=EMBEDDING_MODEL
            ),
            AnthropicSearchTool(
                qdrant_url=QDRANT_URL,
                embedding_model=EMBEDDING_MODEL
            )
        ]
    )

    with open("data/test_dataset.json", "r", encoding="utf-8") as f:
        test_dataset = json.load(f)

    prompt = ChatPromptTemplate.from_messages([
        ("system", EVAL_SYSTEM_TEMPLATE),
        ("user", EVAL_USER_TEMPLATE)
    ])

    eval_chain = prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(EvalResult)

    task_results = await asyncio.gather(*[eval_agent(test_data, agent, eval_chain) for test_data in test_dataset])
    for test_data, (retrieved_contexts_str, generated_answer, eval_result) in zip(test_dataset, task_results):
        test_data["retrieved_contexts"] = retrieved_contexts_str
        test_data["generated_answer"] = generated_answer
        test_data["retrieved_context_score_reasoning"] = eval_result.retrieved_context_score_reasoning
        test_data["generated_answer_score_reasoning"] = eval_result.generated_answer_score_reasoning
        test_data["retrieved_context_score"] = eval_result.retrieved_context_score
        test_data["generated_answer_score"] = eval_result.generated_answer_score

    df = pd.DataFrame(test_dataset)
    metric = {
        "retrieved_context_score_mean": df["retrieved_context_score"].mean(),
        "generated_answer_score_mean": df["generated_answer_score"].mean()
    }
    eval_result_dir = f"eval_result/{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(eval_result_dir, exist_ok=True)
    df.to_csv(f"{eval_result_dir}/test_dataset_eval.csv", index=False)
    with open(f"{eval_result_dir}/metric.json", "w", encoding="utf-8") as f:
        json.dump(metric, f, ensure_ascii=False, indent=4)
    

if __name__ == "__main__":
    asyncio.run(main())