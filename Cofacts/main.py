import requests
import mysql.connector
import os


def getArticles():
    url = "https://api.cofacts.tw/graphql"
    query = """
    query MyQuery($first: Int) {
      ListArticles(first: $first) {
        edges {
          node {
            id
            text
            articleReplies {
              reply {
                id
                text
                type
              }
            }
          }
        }
      }
    }
    """
    variables = {"first": 10000}

    response = requests.post(
        url,
        json={"query": query, "variables": variables},
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        data = response.json()
        articles = data["data"]["ListArticles"]["edges"]
        return articles
    else:
        return None


def dealTrueorFalse(articleReplies):
    # reply example
    # "reply": {
    #     "id": "9yZcVIABvUvLpBdgpVXu",
    #     "text": "這是2020 年的舊聞，並非2022 年的事件。該地下工廠製成飲品，豆漿、米漿、杏仁茶等，在網路及其他通路販售，已依詐欺罪送辦。",
    #     "type": "RUMOR"
    # }
    # 決定這篇文章是真還是假
    # tpye = RUMOR or NOT_RUMOR or OPINIONATED or NOT_ARTICLE
    times = {
        "RUMOR": 0,
        "NOT_RUMOR": 0,
        "OPINIONATED": 0
    }
    text = {
        "RUMOR": [],
        "NOT_RUMOR": [],
        "OPINIONATED": []
    }
    for reply in articleReplies:
        if reply["reply"]["type"] == "RUMOR":
            times["RUMOR"] += 1
            text["RUMOR"].append(reply["reply"]["text"])
            text["OPINIONATED"].append(reply["reply"]["text"])
        elif reply["reply"]["type"] == "NOT_RUMOR":
            times["NOT_RUMOR"] += 1
            text["NOT_RUMOR"].append(reply["reply"]["text"])
            text["OPINIONATED"].append(reply["reply"]["text"])
        elif reply["reply"]["type"] == "OPINIONATED":
            times["OPINIONATED"] += 1
            text["OPINIONATED"].append(reply["reply"]["text"])
    if times["RUMOR"] > times["NOT_RUMOR"]:
        return "Not_Rumor", text["RUMOR"]
    elif times["NOT_RUMOR"] > times["RUMOR"]:
        return "Rumor", text["NOT_RUMOR"]
    else:
        return "Fuzzy", text["OPINIONATED"]


def dealData(articles):
    for article in articles:
        title = None
        summary = None
        content = article["node"]["text"]
        url = article['node']["id"]
        (trueorfalse, accordingto) = dealTrueorFalse(
            article['node']['articleReplies'])
        store_to_db(title, summary, content, url, trueorfalse, accordingto)


def store_to_db(title, summary, content, url, trueorfalse, accordingto):
    # 將 192.168.50.103 替換為你的 Windows IP 位址
    db_host = "host.docker.internal"
    db_name = "spider"
    db_act = "root"
    db_pass = ""
    db_port = 3306  # 預設的 MySQL 端口

    conn = mysql.connector.connect(
        host=db_host,
        user=db_act,
        password=db_pass,
        database=db_name,
        port=db_port
    )

    if conn.is_connected():
        print("成功連線到 MySQL 資料庫!")

    cursor = conn.cursor()

    query = """
    INSERT INTO article (title, summary, content, url, trueorfalse, accordingto)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    cursor.execute(query, (title, summary, content, url,
                   trueorfalse, ', '.join(accordingto)))

    article_id = cursor.lastrowid
    fromwhere = "Cofacts"
    query_article_type = """
    INSERT INTO article_type (article_id, fromwhere)
    VALUES (%s, %s)
    """
    try:
        cursor.execute(query_article_type, (article_id, fromwhere))
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        conn.rollback()
    conn.commit()
    cursor.close()
    conn.close()
    print(title, summary, content, url, trueorfalse, accordingto)


article = getArticles()
dealData(article)
