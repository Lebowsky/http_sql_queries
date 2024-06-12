import uvicorn
from pydantic import BaseModel

import sqlite3
from sqlite3 import Error

from fastapi import FastAPI
from starlette.responses import PlainTextResponse

app = FastAPI()


class Query(BaseModel):
    mode: str
    query: str
    params: str = ''
    db_name: str


@app.post("/")
def sql_query(mode: str, query: str, params: str, db_name: str):
    res = get_query_result(query, params)
    return PlainTextResponse(res)


db_path = 'rightscan5.db'
conn = None


def get_query_result(query_text: str, params="") -> str:
    try:
        conn = sqlite3.connect(db_path)
    except Error:
        raise ValueError('No connection with database')

    cursor = conn.cursor()
    try:
        if params:
            args = params.split(',')
            cursor.execute(query_text, args)
        else:
            cursor.execute(query_text)
    except Exception as e:
        raise e

    res = cursor.fetchall()

    data = ['|'.join([column[0] for column in cursor.description])]

    for row in res:
        data.append('|'.join([str(v) for v in row]))

    conn.commit()
    conn.close()
    return '\r\n'.join(data)


if __name__ == '__main__':
    uvicorn.run(app=app, port=8095)
