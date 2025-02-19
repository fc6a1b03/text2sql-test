import sys
import re
import os
from operator import itemgetter
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
from langchain_community.tools import QuerySQLDatabaseTool  # 修正导入
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

def clean_sql(raw_sql):
    """增强SQL清洗逻辑"""
    # 匹配更广泛的SQL语句模式
    match = re.search(r'```sql\n(.*?)\n```|(SELECT|INSERT|UPDATE|DELETE).*', raw_sql, re.DOTALL|re.IGNORECASE)
    return match.group(0).replace('```sql','').strip() if match else raw_query

# 初始化数据库（使用绝对路径）
db_path = os.path.join(os.getcwd(), "Chinook.db")
db = SQLDatabase.from_uri(f"sqlite:///{db_path}")

# 配置DeepSeek模型
llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("API_KEY"),
    base_url="https://api.deepseek.com/v1",
    temperature=0  # 确保输出稳定性
)

# 创建带验证的查询链
query_tool = QuerySQLDatabaseTool(db=db)  # 修正类名
chain = (
    RunnablePassthrough.assign(query=create_sql_query_chain(llm, db))
    | itemgetter("query")
    | query_tool
)

def main():
    try:
        question = sys.argv[1] if len(sys.argv) > 1 else "How many employees are there?"
        print(f"[执行问题] {question}")
        
        # 执行完整链式调用
        result = chain.invoke({"question": question})
        print(f"[最终答案] {result}")
    except Exception as e:
        print(f"[严重错误] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
