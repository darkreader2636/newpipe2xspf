# NewPipe2xspf A quick script that I threw together for exporting NewPipe Playlists to VLC

import sqlite3
from typing import Tuple, List
from functools import wraps
import xspf
import xml.dom.minidom
from datetime import datetime
import sys

x = xspf.Xspf()

Playlist = Tuple[int, str, int, int]  # 0:Playlist ID 1:Playlist Name 2:is_thumbnail_permanent 3:thumb_stream_id

Video = Tuple[int ,int ,str ,str ,str , int ,str ,str ,str ,int ,str ,int ,int] #Don't ask me look at streams table on newpipe db

class db_wrapper:
    def __init__(self):
        self.open()

    def open(self):
        """Initializes the database"""
        try:
            self.conn = sqlite3.connect(sys.argv[1])
            self.cur = self.conn.cursor()
            self.cur.execute("SELECT * FROM playlists")
        except:
            print(f"Error: Cannot find database file")
            exit(1)
        

    def close(self):
        """Safely closes the database"""
        if self.conn:
            self.conn.commit()
            self.cur.close()
            self.conn.close()

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
    db = db_wrapper() #Connect to DB

    print("Select Local Playlist Name:\n")
    crt_list = db.get_playlist()
    for pl_list in enumerate(crt_list):
        print(f"{pl_list[0]+1}: {pl_list[1][1]}")
    print("0: Exit")

    input_id = int(input(">")) -1

    if(input_id == -1):
        exit(0)

    selected = crt_list[input_id][0]
    x.title = crt_list[input_id][1]
    x.info = "Exported with NewPipe2xspf"

    vid_list = []

    for uid in db.get_streams(selected):
        vid_list.append(db.get_video(uid[1]))

    for vid in enumerate(vid_list):
        tr1 = xspf.Track()
        tr1.trackNum = str(vid[0] + 1)
        vid = vid[1][0]
        tr1.location = vid[2]
        tr1.title = vid[3]
        tr1.duration = str(vid[5]*1000)
        tr1.creator = vid[6]
        tr1.image = vid[8]
        tr1.annotation = vid[2]
        x.add_track(tr1)

    xmldata = x.toXml()
    m2 = xml.dom.minidom.parseString(xmldata).toprettyxml()

    time = datetime.now().strftime("%H.%M_%d-%b-%Y")
    filename = f"{crt_list[input_id][1].replace(' ', '_')}_{time}.xspf"

    with open(filename, "w") as f:
        f.write(m2)

    db.close()

while True:
    main()