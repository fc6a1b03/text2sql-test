import sys
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
import os

def get_question():
    """处理输入参数"""
    if len(sys.argv) > 1:
        return sys.argv[1]
    else:
        # 本地运行时提示输入
        if os.getenv("GITHUB_ACTIONS") != "true":
            return input("请输入查询问题：")
        else:
            print("Error: 需要提供问题参数")
            sys.exit(1)

# 初始化数据库和模型
db = SQLDatabase.from_uri("sqlite:///Chinook.db") 
llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("API_KEY"),
    base_url="https://api.deepseek.com/v1"
)
chain = create_sql_query_chain(llm, db)

def main():
    question = get_question()
    try:
        query = chain.invoke({"question": question})
        result = db.run(query)
        print(f"\n=== 执行结果 ===\n问题：{question}\nSQL：{query}\n结果：{result}")
    except Exception as e:
        print(f"\n错误：{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
