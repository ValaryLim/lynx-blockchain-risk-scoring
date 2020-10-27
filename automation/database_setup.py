import sqlite3

conn = sqlite3.connect(r"../automation/lynx_data.db")
c = conn.cursor()

c.execute('''CREATE TABLE POST_DATA(
        uid TEXT PRIMARY KEY NOT NULL,
        sourceID TEXT,
        source VARCHAR(20) NOT NULL,
        article_date DATETIME,
        content TEXT NOT NULL,
        url TEXT NOT NULL, 
        count INT NOT NULL,
        img_link TEXT,
        entity VARCHAR(50) NOT NULL,
        author VARCHAR(50),
        ground_truth_risk INT NOT NULL,
        probability_risk FLOAT NOT NULL,
        predicted_risk FLOAT NOT NULL,
        coin TEXT)''')

conn.commit()

c.execute('''CREATE TABLE ENTITY_DATA(
        entity VARCHAR(50) NOT NULL,
        date DATE NOT NULL,
        score INT NOT NULL)''')
conn.commit()

conn.close()

