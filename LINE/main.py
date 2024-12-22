import requests
import mysql.connector


def dealTrueorFalse(article):
    if (len(article["comments"]) == 0):
        accredited = None
    else:
        accredited = article["comments"][0]["content"] + \
            "*****url:"+article["comments"][0]["url"]
    # print(accredited)
    if (article["tag"]["en"] == "Unreal"):
        return ("Rumor", accredited)
    elif (article["tag"]["en"] == "Partial Real"):
        return ("Rumor", accredited)
    else:
        return ("Not_Rumor", accredited)


def getArticles(page):
    print("page", page)
    url = "https://api-fact-checker.line-apps.com/pub/v1/zhtw/articles/latest?size=12&sort=updatedAt,desc&page="
    response = requests.get(url + str(page))
    if response.json().get("last"):
        print("last page")
        return 0
    articles = response.json().get("content")
    for article in articles:
        title = None
        summary = None
        content = article["content"]
        url = "https://fact-checker.line.me/news?categoryId=" + \
            str(article["category"]["id"]) + "&articleId=" + str(article["id"])
        (trueorfalse, accordingto) = dealTrueorFalse(article)
        store_to_db(title, summary, content, url, trueorfalse, accordingto)
    return 1


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
                   trueorfalse, accordingto))

    article_id = cursor.lastrowid
    fromwhere = "Line"
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


for i in range(12, 10000):
    n = getArticles(i)
    if not n:
        break
