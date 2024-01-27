import sqlite3
from typing import Tuple, List
from functools import wraps
import xspf
import xml.dom.minidom
x = xspf.Xspf()

Playlist = Tuple[int, str, int, int]  # 0:Playlist ID 1:Playlist Name 2:is_thumbnail_permanent 3:thumb_stream_id

Video = Tuple[int ,int ,str ,str ,str , int ,str ,str ,str ,int ,str ,int ,int]    

class db_wrapper:
    def __init__(self):
        self.open()

    def open(self):
        """Initializes the database"""
        self.conn = sqlite3.connect('newpipe.db')
        self.cur = self.conn.cursor()

    def close(self):
        """Safely closes the database"""
        if self.conn:
            self.conn.commit()
            self.cur.close()
            self.conn.close()

    def _commit(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            self.conn.commit()
            return result
        return wrapper

    def get_playlist(self) -> Playlist:
        self.cur.execute(
            "SELECT * FROM playlists",
        )
        result = self.cur.fetchall()
        if result:
            return result

    def get_streams(self, list_id: int) -> list:
        self.cur.execute(
            "SELECT * FROM playlist_stream_join WHERE playlist_id=? ORDER BY join_index ASC",
            (str(list_id),)
        )
        result = self.cur.fetchall()
        if result:
            return result

    def get_video(self, uuid: int) -> Video:
        self.cur.execute(
            "SELECT * FROM streams WHERE uid=?",
            (str(uuid),)
        )
        result = self.cur.fetchall()
        if result:
            return result

def main():
    db = db_wrapper()
    i = 1

    print("sel list:\n")
    crt_list = db.get_playlist()
    for pl_list in crt_list:
        print(f"{i}:{pl_list[1]}")
        i = i+1

    input_id = int(input(">")) -1
    selected = crt_list[input_id][0]
    x.title = crt_list[input_id][1]
    x.info = "Exported with NewPipe2XSPF"

    mangled = db.get_streams(selected)

    my_list = []
    for uid in mangled:
        my_list.append(db.get_video(uid[1]))

    i = 1

    for vid in my_list:
        tr1 = xspf.Track()
        tr1.trackNum = str(i)
        tr1.location = vid[0][2]
        tr1.title = vid[0][3]
        tr1.duration = str(vid[0][5]*1000)
        tr1.creator = vid[0][6]
        tr1.image = vid[0][8]
        x.add_track(tr1)
        i = i+1

    xmldata = x.toXml()
    m2 = xml.dom.minidom.parseString(xmldata).toprettyxml()

    with open("new.xspf", "w") as f:
        f.write(m2)

    db.close()

while True:
    main()