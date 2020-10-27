#alvin.mingguw@gmail.com

#install modul tweepy
#conda install -c conda-forge tweepy
#pip install tweepy

import tweepy
import pandas as pd
import csv
import re #regex
import string
import sqlite3
from keys import a0_twitter_keys as keys #memanggil file berisi key Twitter API yang sudah dibuat terpisah dari script ini
from datetime import date, timedelta
# import datetime
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

def tweepy_credents():
    global api
    auth = tweepy.OAuthHandler(keys.consumer_key, keys.consumer_secret)
    auth.set_access_token(keys.access_token, keys.access_token_secret)
    # api = tweepy.API(auth)
    api = tweepy.API(auth,wait_on_rate_limit=True)

    try:
        api.verify_credentials()
        print("Authentication OK\n\n")
    except:
        print("Error during authentication\n\n")

# def get_tweets(keyword):
def get_tweets(keyword):
    global df
    global list_df
    # global keyword
    global search_words
    global search_words_trim
    global tanda_bantu
    tanda_bantu = "'"
    global date_until
    #Validasi input range banyak hari yang diambil, minimal 1 hari, max 7 hari
    isMax7Days = False
    import datetime
    while not isMax7Days:
        try:
            since_days_length = int(input('Masukan Banyak hari ke belakang yang akan diambil (Max 7 Hari kebelakang)'))
            if since_days_length >= 0 and since_days_length <= 7:
                isMax7Days = True
        except:
            print('You must enter a valid number between 1 and 7')
        #Reference: http://easypythondocs.com/validation.html

    #ini untuk menangkap otomatsi date hari ini & date since yang sebelumnya di input
    date_since = date.today() - timedelta(days=(since_days_length))
    date_since = date_since.strftime("%Y-%m-%d")
    # print("date_since =", date_since)

    date_until = date.today()
    date_until = date_until.strftime("%Y-%m-%d")
    # print("date_until (today) =", date_until)
    print(f'Mengambil data tweet dengan topik : {keyword}')
    print(f'Periode : {date_since} s/d {date_until}\n')


    search_words = keyword #<--KEYWORD YANG DIPAKAI
    # search_words = 'vaksin covid' #<--KEYWORD YANG DIPAKAI
    # search_words_trim = print(search_words.replace(' ',''))
    # search_words2 = print(f'{search_words}')
    # search_words2
    # date_since = "2020-09-07"
    # date_until = "2020-09-12"
    total_tweet = 5 #<-sebagai limiter

# Returns a timeline of tweets authored by members of the specified list.
# Retweets are included by default.
# Use the include_rts=false parameter to omit retweets.

    new_search = search_words + " -filter:retweets"
    tweets = tweepy.Cursor(api.search,
            q=new_search,
            lang="id",
            since=date_since,
            until=date_until,
            result_type='recent',
            include_rts='false',
            tweet_mode="extended").items(total_tweet) #<-- karena acuannya tanggal, total tweet tdk dimasukan ke dalam items() / tidak diberi angka.

    # list_until = []
    # list_topic = []
    # list_until


    list_id=[]
    list_username=[]
    list_date=[]
    list_tweets=[]
    for tweet in tweets:
        list_id.append(tweet.id)
        list_username.append('@' + tweet.user.screen_name)
        list_date.append(tweet.created_at)
        list_tweets.append(tweet.full_text)

    #menyimpan kolom tweets tanpa cleansing (regex versi 1 ataupun versi 2 / sastrawi) ke dalam kolom 'tweets'

        df = pd.DataFrame(list(zip(list_id, list_username, list_date, list_tweets)), 
                    columns =['tweetid', 'username', 'date', 'tweets'])

    #memproses kolom tweets dengan regex versi 1 dan menyimpan ke dalam kolom baru bernama 'tweets_cleaned'

    def hapus_tanda(tweet): 
        tanda_baca = set(string.punctuation)
        tweet = ''.join(ch for ch in tweet if ch not in tanda_baca)
        return tweet
    
    def hapus_katadouble(s): 
        pattern = re.compile(r"(.)\1{1,}", re.DOTALL)
        return pattern.sub(r"\1\1", s)
    
    list_clean_tweets = []
    for tweet in df.tweets:
        tweet = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",tweet).split())
        # list_clean_tweets.append(clean_tweets.lower())
        tweet=tweet.lower()
        tweet = re.sub(r'\\u\w\w\w\w', '', tweet)
        tweet=re.sub(r'http\S+','',tweet)
        #hapus @username
        tweet=re.sub('@[^\s]+','',tweet)
        #hapus #tagger 
        tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
        #hapus tanda baca
        # tweet=hapus_tanda(tweet) #<-sering menghapus kata covid
        #hapus angka dan angka yang berada dalam string 
        tweet=re.sub(r'\w*\d\w*', '',tweet).strip()
        #hapus repetisi karakter 
        tweet=hapus_katadouble(tweet)
        ## stemming
        # factory = StemmerFactory()
        # stemmer = factory.create_stemmer()
        # tweet = stemmer.stem(tweet)
        list_clean_tweets.append(tweet)

    df['tweets_cleaned'] = list_clean_tweets
    # display(df)

    list_clean_tweets_sastrawi = []
    for tweet in df.tweets_cleaned:
        # tweet=tweet.lower()
        # tweet = re.sub(r'\\u\w\w\w\w', '', tweet)
        # tweet=re.sub(r'http\S+','',tweet)
        # #hapus @username
        # tweet=re.sub('@[^\s]+','',tweet)
        # #hapus #tagger 
        # tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
        # # hapus tanda baca
        # tweet=hapus_tanda(tweet) #<-sering menghapus kata covid
        # #hapus angka dan angka yang berada dalam string 
        # tweet=re.sub(r'\w*\d\w*', '',tweet).strip()
        # #hapus repetisi karakter 
        # tweet=hapus_katadouble(tweet)
        #stemming
        factory = StemmerFactory()
        stemmer = factory.create_stemmer()
        tweet = stemmer.stem(tweet)
        list_clean_tweets_sastrawi.append(tweet)

    df['tweets_cleaned_sastrawi'] = list_clean_tweets_sastrawi
    df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.normalize()
    df['date'] = df['date'].astype('str')

    df['topic_id'] = ''
    df['sentiment'] = ''
    df['label'] = ''
    df['date_added'] = date_until

    df = df[['topic_id', 'tweetid', 'username', 'date', 'date_added', 'tweets', 'tweets_cleaned', 'tweets_cleaned_sastrawi', 'sentiment', 'label']]

    # df = df[['tweetid', 'tweet']]
    display(df)

    # df.to_excel(r'data.xlsx', index = False)
    # df.to_csv(r'data.csv', index = False)
    list_df = df.values.tolist()
    
# def create():
#     try:
#         c.execute("""CREATE TABLE IF NOT EXISTS tweepy(
#         tweetid varchar PRIMARY KEY,
#         username varchar,
#         date text,
#         tweets varchar,
#         tweets_cleaned varchar,
#         tweets_cleaned_sastrawi varchar);
#         """)
#     except:
#         pass

# def insert():
#     c.execute("""INSERT OR IGNORE INTO tweepy (tweetid, username, date, tweets, tweets_cleaned, tweets_cleaned_sastrawi)
#             values(df.tweetid, df.username, df.date, df.tweets, df.tweets_cleaned, df.tweets_cleaned_sastrawi)""")

# def select(verbose=True):
#     sql = "SELECT * FROM tweepy"
#     recs = c.execute(sql)
#     if verbose:
#         for row in recs:
#             print(row)

def connection_sql():    
    global c
    global conn
    db_path = r'./database/alvin.mingguw.db'
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

def create_table():
    # conn = sqlite3.connect('alvin.mingguw.db')
    # c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS tweepy(
        topic_id INT,
        tweetid TEXT(19) PRIMARY KEY NOT NULL,
        username TEXT(50) NOT NULL,
        date DATE NOT NULL,
        date_added DATE NOT NULL,
        tweets TEXT(300) NOT NULL,
        tweets_cleaned TEXT(300) NOT NULL,
        tweets_cleaned_sastrawi TEXT(300) NOT NULL,
        sentiment int(2),
        label int(1));
        """)
    print("Table tweepy created successfully")

    c.execute("""CREATE TABLE IF NOT EXISTS topics(
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        topic TEXT (50) NOT NULL UNIQUE,
        date_added TEXT NOT NULL);
        """)

    # c.execute("""CREATE TABLE IF NOT EXISTS topics (
	# id	INTEGER NOT NULL,
	# topics	TEXT(50) NOT NULL UNIQUE,
	# date_added	TEXT NOT NULL,
	# PRIMARY KEY(id AUTOINCREMENT));
    # """)
    print("Table topics created successfully")
    conn.commit()

    # c.execute("""CREATE TABLE IF NOT EXISTS sqlite_sequence(
    # name,
    # seq);
    # """)
    # conn.commit()

def insert_data():
    # conn = sqlite3.connect('alvin.mingguw.db')
    # c = conn.cursor()
    c.executemany("INSERT OR IGNORE INTO tweepy VALUES (?,?,?,?,?,?,?,?,?,?);", list_df)
    print("Records tweepy inserted successfully")
    conn.commit()

    # c.executemany("INSERT OR IGNORE INTO topics (id, topics, date_added) VALUES (?, ?,?);", (1, search_words, date_until))
    c.execute("INSERT OR IGNORE INTO topics VALUES (NULL,?,?);", (search_words, date_until))
    print("Records topics inserted successfully")
    conn.commit()

    # c.execute(f'''UPDATE tweepy
    #         SET topic_id = (SELECT id
    #         FROM topics
    #         WHERE topics.topics = {tanda_bantu+search_words+tanda_bantu});''')

    # c.execute(f'''UPDATE tweepy
    #         SET topic_id = (SELECT id
    #         FROM topics
    #         WHERE (tweepy.topic_id is null or tweepy.topic_id = '') AND topics.topics = {tanda_bantu+search_words+tanda_bantu});''')

    c.execute(f'''UPDATE tweepy
            SET topic_id = (SELECT id
            FROM topics WHERE topic = {tanda_bantu+search_words+tanda_bantu})
            WHERE (tweepy.topic_id is null or tweepy.topic_id = '');''')

    # c.execute('''UPDATE tweepy
    #         SET topic_id = (SELECT id
    #         FROM topics
    #         WHERE (tweepy.topic_id is null or tweepy.topic_id = '') AND replace(topics.topics, ' ','') = ? );''',(search_words))
    # c.execute('''UPDATE tweepy
    #         SET topic_id = (SELECT id
    #         FROM topics
    #         WHERE tweepy.topic_id = '' AND replace(topics.topics, ' ','') = ? );''',(search_words.replace(' ','')))

    # c.execute(f'''UPDATE tweepy
    #         SET topic_id = (SELECT id
    #         FROM topics
    #         WHERE tweepy.topic_id = '' AND topics.topics = {search_words});''')
    conn.commit()
    print('\nUpdate id topic Berhasil')

def show_table_data():
    # conn = sqlite3.connect('alvin.mingguw.db')
    # c = conn.cursor()
    c.execute('SELECT * FROM tweepy')
    return print(c.fetchall())

def close():
    # conn = sqlite3.connect('alvin.mingguw.db')
    # c = conn.cursor()    
    c.close()
    conn.close()

            

# tweepy_credents()
# get_tweets('vaksin covid') #<--KEYWORD YANG DIPAKAI
# connection_sql()
# create_table()
# insert_data()
# show_table_data()
# close()