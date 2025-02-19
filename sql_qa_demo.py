import sys, re, os
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
from langchain_community.tools import QuerySQLDatabaseTool

def clean_sql(raw_sql):
    patterns = [r'```sql\n(.*?)\n```', r'(SELECT.*)', r'^SQLQuery:\s*(.*)']
    for p in patterns:
        match = re.search(p, raw_sql, re.DOTALL|re.IGNORECASE)
        if match: 
            return match.group(1 if p == patterns[2] else 0).strip()
    return raw_sql

# 初始化数据库（使用绝对路径）
db_path = os.path.join(os.getcwd(), "Chinook.db")
db = SQLDatabase.from_uri(f"sqlite:///{db_path}")

# 配置 DeepSeek 模型
llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("API_KEY"),
    base_url="https://api.deepseek.com/v1",
    temperature=0
)

# 创建带验证的查询链
chain = create_sql_query_chain(llm, db)
query_tool = QuerySQLDatabaseTool(db=db)

def main():
    question = sys.argv[1] if len(sys.argv) > 1 else "How many employees?"
    try:
        raw_query = chain.invoke({"question": question})
        query = clean_sql(raw_query)
        print(f"[生成SQL] {query}")
        query_tool.invoke(query) 
        result = db.run(query)
        print(f"[答案] {result}")
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    main()
