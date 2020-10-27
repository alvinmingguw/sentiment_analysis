import sqlite3
import pandas as pd
import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import a1_update_data as menu1


#FUNGSI UPDATE SENTIMEN
def update_sentiment():
    print("Update Data Sentiment")
    print(f'Topik : {menu1.search_words}')
    conn = sqlite3.connect('./database/alvin.mingguw.db')
    c = conn.cursor()
    # df = pd.read_excel("data.xlsx")
    # df = pd.read_sql_query("SELECT * from tweepy", conn)
    df = pd.read_sql_query("SELECT * from tweepy WHERE sentiment = ''", conn)
    # df = pd.read_sql_query(f'''SELECT * from view_tweepy WHERE
    #                          date BETWEEN {menu1.date_since} AND {menu1.search_words} AND topic = {menu1.date_until}''',conn)
    # df=df.reset_index()
    # df=df.drop(['index'],axis=1)
    # df.reset_index(inplace=True)
    # display(df)
    word_token = df['tweets_cleaned_sastrawi'].tolist()
    print(word_token)

    pos_list= open("./sentiment/kata_positif.txt","r")
    pos_kata = pos_list.readlines()
    neg_list= open("./sentiment/kata_negatif.txt","r")
    neg_kata = neg_list.readlines()

    S = []
    for item in word_token:
        count_p = 0
        count_n = 0
        for kata_pos in pos_kata:
            if kata_pos.strip() in item:
                count_p +=1
        for kata_neg in neg_kata:
            if kata_neg.strip() in item:
                count_n +=1
    # print ("positif: "+str(count_p))
    # print ("negatif: "+str(count_n))
        S.append(count_p - count_n)

    print(S)

    S_new = []
    for a in S:
        if a<0:
            a=0
        else:
            a=1
        S_new.append(a)    
    print(S_new)
    
    df['sentiment'] = S
    df['label'] = S_new
    display(df)

    vectorizer = TfidfVectorizer (max_features=2500)
    model_g = GaussianNB()

    v_data = vectorizer.fit_transform(df['tweets_cleaned_sastrawi']).toarray()

    print(v_data)

    X_train, X_test, y_train, y_test = train_test_split(v_data, df['label'], test_size=0.2, random_state=0)
    model_g.fit(X_train,y_train)

    y_preds = model_g.predict(X_test)
    y_label = model_g.predict(v_data)
    print(y_label)

    print(confusion_matrix(y_test,y_preds))
    print(classification_report(y_test,y_preds))
    print('nilai akurasinya adalah ',accuracy_score(y_test, y_preds))

    tweet = ''
    v_data = vectorizer.transform([tweet]).toarray()
    y_preds = model_g.predict(v_data)


    if y_preds == 1:
        print('Positif')
    else:
        print('Negatif')
  
    df['label'] = y_label
    display(df)
    df = df[['tweetid','sentiment','label']]

    list_df = df.values.tolist()

    # df.to_sql('tweepy_temp', conn, if_exists='replace')

    # conn = sqlite3.connect('alvin.mingguw.db')
    # c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS tweepy_temp(
        tweetid TEXT(19) PRIMARY KEY NOT NULL,
        sentiment int(2) NOT NULL,
        label int(1) NOT NULL);
        """)
    print("Table created successfully")

    # conn = sqlite3.connect('alvin.mingguw.db')
    # c = conn.cursor()
    c.executemany("INSERT OR IGNORE INTO tweepy_temp VALUES (?,?,?);", list_df)
    print("Records created successfully")
    conn.commit()


    # c.execute("""UPDATE tweepy
    #             SET sentiment = (SELECT sentiment
    #             FROM tweepy_temp
    #             WHERE tweepy_temp.tweetid = tweepy.tweetid AND (tweepy.sentiment IS NULL OR tweepy.sentiment = ''));""")
    # print('\nUpdate Sentiment Berhasil')

    # c.execute("""UPDATE tweepy
    #             SET label = (SELECT label
    #             FROM tweepy_temp
    #             WHERE tweepy_temp.tweetid = tweepy.tweetid AND (tweepy.label IS NULL OR tweepy.label = ''));""")
    # print('Update Label Berhasil\n')

    c.execute("""UPDATE tweepy
                SET sentiment = (SELECT sentiment
                FROM tweepy_temp
                WHERE tweepy_temp.tweetid = tweepy.tweetid)
                WHERE (tweepy.sentiment = '' OR tweepy.sentiment IS NULL);""")
    print('\nUpdate Sentiment Berhasil')

    c.execute("""UPDATE tweepy
                SET label = (SELECT label
                FROM tweepy_temp
                WHERE tweepy_temp.tweetid = tweepy.tweetid)
                WHERE (tweepy.label = '' OR tweepy.label IS NULL);""")
    print('Update Label Berhasil\n')
  
    conn.commit()
    c.close()
    conn.close()

# update_sentiment()