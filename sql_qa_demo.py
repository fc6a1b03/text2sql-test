# sql_qa_demo.py
import re, sys
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
import os

def clean_sql(raw_sql):
    match = re.search(r'(SELECT|INSERT|UPDATE|DELETE).*', raw_sql, re.IGNORECASE | re.DOTALL)
    return match.group(0) if match else raw_sql

db = SQLDatabase.from_uri(
    "sqlite:///Chinook.db",
    include_tables=['Employee'],
    custom_table_info={
        "Employee": "Table with employees, columns: EmployeeId, LastName, FirstName, ..."
    }
)

llm = ChatOpenAI(model="deepseek-chat", api_key=os.getenv("API_KEY"), base_url="https://api.deepseek.com/v1")
chain = create_sql_query_chain(llm, db)
query_tool = QuerySQLDataBaseTool(db=db)

def run_qa(question):
    try:
        raw_query = chain.invoke({"question": question})
        query = clean_sql(raw_query)
        print(f"[原始SQL] {raw_query}")  # 调试输出
        query_tool.invoke(query)  # 验证SQL
        result = db.run(query)
        print(f"[结果] {result}")
    except Exception as e:
        print(f"执行失败: {str(e)}")

if __name__ == "__main__":
    run_qa(sys.argv[1] if len(sys.argv)>1 else "How many employees?")
