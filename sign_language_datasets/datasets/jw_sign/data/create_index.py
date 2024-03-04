"""Helper file to crawl The Jehovah Witness Sign Language Website and create an up-to-date index of the dataset
May wish to install reqs first, something like: 
conda create -n jw_sign_create_index pip # create a miniconda env with pip inside it
conda activate jw_sign_create_index # activate the env
python -m pip install -r create_index_requirements.txt # use the pip which is IN the env to install requirements IN the env
"""

# !pip3 install requests-html # Colin Leong/CDL: commented out, doesn't work in a .py
import pandas as pd
import urllib
import pickle
import gzip
import json
import subprocess
from requests_html import HTMLSession
from urllib.request import urlopen
from urllib.error import HTTPError
from tqdm import tqdm
import argparse
from pathlib import Path

import time  # for time.sleep(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script to create index for JWSign dataset"
    )
    parser.add_argument(
        "--valid_verse_ids_json",
        type=Path,
        default=Path("tkl.json"),
        help="""JSON containing list of valid verse IDs (default: tkl.json). e.g. ["v4004026", "v19146003", "v4005020"]""",
    )
    parser.add_argument(
        "--sign_lang_codes_to_spoken_lang_codes_json",
        type=Path,
        default=Path("s2t.json"),
        help="""Json with pairs of language codes (default: s2t.json). e.g. {"ALS": "sq", "ASL": "en",...}""",
    )

    parser.add_argument(
        "--text_dict_json",
        type=Path,
        default=Path("text_dict.json"),
        help="""
                        JSON to link text-language codes with common names, and jw.org urls (default: text_dict.json).
                        e.g.
{"en": {"lang_ini": "en", "lang_nme": "english", "base_url": "https://www.jw.org/en/library/bible/nwt/books/"}, 
"es": {"lang_ini": "es", "lang_nme": "spanish", "base_url": "https://www.jw.org/es/biblioteca/biblia/nwt/libros/"}, ...}""",
    )
    parser.add_argument(
        "--valid_signs_json",
        type=Path,
        default=Path("valid_signs.json"),
        help="""JSON containing a list of language codes for sign languages (default: valid_signs.json). e.g. ["ALS", "ASL", "LAS",...]""",
    )

    parser.add_argument(
        "--user_sign", type=str, default="ALL_LANGS", help="""Specify three-letter code you wish to scrape, or ALL_LANGS to scrape every code listed in valid_signs_json (default: ALL_LANGS)"""
    )
    args = parser.parse_args()

    tks = json.loads(
        open(str(args.valid_verse_ids_json), "r").read()
    )  #'en': ... # CDL: list of valid verse IDs
    s2t = json.loads(
        open(str(args.sign_lang_codes_to_spoken_lang_codes_json), "r").read()
    )  #'JML': 'en'     # CDL: pairs of language codes (e.g. "ASL":"en", and also "WSL":"en"). s2t means signed to text I believe?
    text_dict = json.loads(
        open(str(args.text_dict_json), "r").read()
    )  # CDL: JSON to link text-language codes with common names, and jw.org urls, e.g. {"en": {"lang_ini": "en", "lang_nme": "english", "base_url": "https://www.jw.org/en/library/bible/nwt/books/"}, "es": {"lang_ini": "es", "lang_nme": "spanish", "base_url": "https://www.jw.org/es/biblioteca/biblia/nwt/libros/"},""
    valid_signs = json.loads(
        open(str(args.valid_signs_json), "r").read()
    )  # CDL: A list of language codes for sign languages

    # print(f"Valid Signs: {valid_signs}")

    # CDL: Parameter for which sign language to scrape.
    user_sign = args.user_sign 
    if user_sign in valid_signs:
        sign_language_ini = [user_sign]
    elif user_sign == "ALL_LANGS":
        sign_language_ini = valid_signs
    else:
        print("Invalid Sign")
        raise ValueError(
            f"user_sign: {user_sign} is not in the valid signs: {valid_signs}. Valid signs were loaded from {args.valid_signs_json}"
        )
    
    print(f"Scraping the following languages: {sign_language_ini}")

    # print(args)

    session = HTMLSession()

    #################################
    # text scraping

    print(f"############ Text Scraping for Sign Languages: {sign_language_ini}")
    for slang in tqdm(sign_language_ini, desc="slang"):
        text_lang = s2t[slang]
        text_info = text_dict[text_lang]
        sign_lang_urls = [text_info]

        # sl_text = dict() #sign_language texts i.e. annotations. each key represent a text/spoken language.
        base = "https://www.jw.org"
        # g = 0 # just to keep track
        t1 = 1  # these times are essential to make sure the site doesn't receive too many requests at once.
        for tlang in tqdm(sign_lang_urls, "tlang"):
            tl_dict = dict()  # text language dictionary.
            sl_url = tlang["base_url"]
            books = session.get(sl_url).html.find(".booksContainer")[0].find("a[href]")
            for bk in tqdm(books, desc="books"):
                session = HTMLSession()
                bk_url = base + bk.attrs["href"]
                chapters = session.get(bk_url).html.find("a.chapter")
                for ch in tqdm(chapters, desc="chapters"):
                    ch_url = base + ch.attrs["href"]
                    verses = (
                        session.get(ch_url)
                        .html.find("div#bibleText")[0]
                        .find("span.verse")
                    )
                    for ver in verses:
                        tl_dict[ver.attrs["id"]] = ver.text
                        # g = g + 1
                        # print(f"verse {g} - {ver.attrs['id']}")
                time.sleep(t1)
            # sl_text[tlang["lang_ini"]] = tl_dict
            print("Text done.")
        tks = set(tl_dict.keys())

    #################################
    # videos scraping
    print(f"################ Video Scraping for sign languages {sign_language_ini}")

    index_data = []  # list which will contain all the videos and associated information

    shester = 1
    for slang in tqdm(sign_language_ini, desc="slang"):
        slang_videos = []

        # CDL: Iterate over books of the NWT for this sign language. range() excludes the second value so max it will do is 66.
        # book "0" gives a metadata page.
        for book_num in tqdm(range(1, 67), desc="book_num"):
            new_video = dict()
            try:
                # Example: "https://b.jw-cdn.org/apis/pub-media/GETPUBMEDIALINKS?pub=nwt&langwritten=ASL&txtCMSLang=ASL&booknum=66&alllangs&output=json&fileformat=MP4%2CM4V%2C3GP"
                link = (
                    "https://b.jw-cdn.org/apis/pub-media/GETPUBMEDIALINKS?pub=nwt&langwritten="
                    + slang
                    + "&txtCMSLang="
                    + slang
                    + "&booknum="
                    + str(book_num)
                    + "&alllangs&output=json&fileformat=MP4%2CM4V%2C3GP"
                )
                response = urlopen(link)
            except HTTPError as err:
                print(err.with_traceback)
                continue
            all_data_json = json.loads(response.read())
            data_json = all_data_json["files"][slang]
            video_types = list(data_json.keys())
            for vt in tqdm(video_types, desc="video_types"):
                for vid in tqdm(data_json[vt], desc="vids"):
                    if (
                        vid["label"] == "720p"
                        and vid["frameRate"] == 29.97
                        and vid["duration"] != 0.0
                    ):
                        vid_url = vid["file"]["url"]
                        vid_name = vid_url.split("/")[-1].split(".")[0]

                        # print(f"ffprobe now, with {vid_url}")

                        # CDL: https://ffmpeg.org/ffprobe.html: "ffprobe gathers information from multimedia streams and prints it in human- and machine-readable fashion."
                        # example: https://d34ji3l0qn3w2t.cloudfront.net/739f58b8-2772-4b85-8dd7-63d49bdf0e11/1/nwt_02_Ex_ASL_01_r720P.mp4vids
                        # ffprobe -i https://d34ji3l0qn3w2t.cloudfront.net/739f58b8-2772-4b85-8dd7-63d49bdf0e11/1/nwt_02_Ex_ASL_01_r720P.mp4vids -print_format default -show_chapters -loglevel error -v quiet -of json
                        command = f"ffprobe -i {vid_url} -print_format default -show_chapters -loglevel error -v quiet -of json"
                        result = subprocess.run(command.split(), capture_output=True)
                        # print("ffprobe done")
                        if result.returncode == 0:
                            output = result.stdout.decode("utf-8")
                            data = json.loads(output)
                        else:
                            continue

                        try:
                            ver_all = data["chapters"]
                        except Exception as err:
                            print(err.with_traceback)
                            # TODO: which Exceptions, precisely?
                            # KeyError would happen if "chapters" is not a valid key
                            # NameError if there's no "data" variable
                            continue
                        if len(ver_all) == 0:
                            continue
                        print(f"Video {shester}")
                        shester = shester + 1
                        for ver in tqdm(ver_all, desc="verse"):
                            verse_dict = {}
                            ver_name = ver["tags"]["title"]
                            count_colon = ver_name.count(":")
                            name_split = vid_name.split("_")
                            # ["0-Pub","1-Bknumb","2-Bkname","3-SignLang","4-Chaptnumb","5-Quality"]
                            try:
                                if count_colon == 1:
                                    versenumb = ver_name.rsplit(":", 1)[1]
                                    chaptnumb = name_split[4]
                                elif count_colon == 0:
                                    if name_split[1] in ["31", "57", "63", "64", "65"]:
                                        versenumb = ver_name.rsplit(" ", 1)[1]
                                        chaptnumb = "1"
                                    else:
                                        continue
                                else:  # count_colon 2,3,4,...
                                    continue
                            except Exception as err:
                                print(err.with_traceback)
                                # TODO: which Exceptions are we checking for?
                                pass
                            verse_dict["video_url"] = vid_url
                            verse_dict["video_name"] = vid_name
                            verse_dict["verse_lang"] = name_split[3]
                            verse_dict["verse_name"] = ver_name  # "Mic. 6:8"
                            verse_dict["verse_start"] = ver["start_time"]
                            verse_dict["verse_end"] = ver["end_time"]
                            verse_dict["duration"] = float(ver["end_time"]) - float(
                                ver["start_time"]
                            )
                            verse_dict["verse_unique"] = (
                                name_split[3] + " " + ver_name
                            )  # "ISL Mic. 6:8"
                            try:
                                id = (
                                    "v"
                                    + str(int(name_split[1]))
                                    + str("{:03d}".format(int(chaptnumb)))
                                    + str("{:03d}".format(int(versenumb)))
                                )  # "v33006008"
                            except Exception as err:
                                print(err.with_traceback)
                                # TODO: which specific exceptions are we looking for here?
                                continue
                            if id in tks:
                                verse_dict["verseID"] = id
                                verse_dict["verse_text"] = tl_dict[
                                    id
                                ]  # TODO clean text
                                index_data.append(verse_dict)

    # remove all duplications inclusive
    df = pd.DataFrame.from_dict(index_data)
    df.drop_duplicates(subset="verse_unique", keep=False, inplace=True)
    index_data = df.to_dict("records")

    # store
    jsonString = json.dumps(index_data)
    jsonFile = open(f"{user_sign}.json", "w")
    jsonFile.write(jsonString)
    jsonFile.close()
