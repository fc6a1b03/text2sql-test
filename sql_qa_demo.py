import sys
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
import os

# 初始化数据库连接
db = SQLDatabase.from_uri("sqlite:///Chinook.db") 

# 创建LLM实例
llm = ChatOpenAI(model="gpt-3.5-turbo-0125")

# 创建问答链
chain = create_sql_query_chain(llm, db)

def run_qa(question):
    query = chain.invoke({"question": question})
    result = db.run(query)
    print(f"问题：{question}")
    print(f"生成的SQL：{query}")
    print(f"查询结果：{result}")
    return result

if __name__ == "__main__":
    question = sys.argv[1] if len(sys.argv) > 1 else "默认问题"
    run_qa(question)
