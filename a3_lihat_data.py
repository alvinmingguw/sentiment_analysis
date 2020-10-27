import sqlite3
from datetime import date, timedelta
import a1_update_data as menu1
# from a1_update_data import search_words

#FUNGSI LIHAT DATA
def lihat_data():
    print("Lihat Data\n")
    print(f'Topik : {menu1.search_words}')
    # anykey=input("Tekan apapun untuk kembali ke menu")
    since= input('Masukan tanggal mulai (format : YYYY-MM-DD)')
    until= input('Masukan tanggal akhir (format : YYYY-MM-DD)')
    # def dict_factory(cursor, row):
    #     d = {}
    #     for idx, col in enumerate(cursor.description):
    #         d[col[0]] = row[idx]
    #     return d
 
    conn = sqlite3.connect('./database/alvin.mingguw.db')
    c = conn.cursor()
    # rows = c.execute("SELECT tweetid, username, date, tweets_cleaned_sastrawi FROM tweepy where date >= ? and date <= ?",[since,until])
    # return print(c.fetchall())
    # rows = c.execute("SELECT tweetid, username, date, tweets_cleaned_sastrawi FROM tweepy where date = ? OR (date BETWEEN ? AND ?)",[since,since,until])

    # c.execute("SELECT COUNT(tweetid) FROM tweepy where date >= ? and date <= ?",[since,until])
    c.execute("SELECT COUNT(tweetid) FROM view_tweepy where date BETWEEN ? AND ? AND topic = ?",[since,until,menu1.search_words])
    if str(c.fetchall())[2] == '0':
        print("Tidak ada data dalam rentang waktu yang dipilih, silahkan coba rentang waktu lain.")
    else :
        print(f'Periode : {since} s/d {until}')
        print('Tweet dibawah ini sudah melalui proses cleansing & stemming sastrawi\n')
        rows = c.execute("SELECT topic, tweetid, username, date, tweets_cleaned_sastrawi FROM view_tweepy where date BETWEEN ? AND ? AND topic = ?",[since,until,menu1.search_words])

        for row in rows:
            print("TweetID = ", row[1])       
            print("Username = ", row[2])
            print("Date = ", row[3])
            print("Tweet = ", row[4])
            print('-------------------------\n')

    # return print(c.fetchall())
    conn.commit()
    c.close()
    conn.close()
    # anykey=input("Tekan apapun untuk kembali ke menu")
    # mainMenu()

# lihat_data()