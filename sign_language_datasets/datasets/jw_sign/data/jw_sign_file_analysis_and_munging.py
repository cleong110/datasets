import pickle
import gzip
import json
from pathlib import Path
import langcodes
import random
import pandas as pd

# copied from the JSON -CDL
# _SIGN_TO_SPOKEN = {
#     "ALS": "sq",
#     "ASL": "en",
#     "LAS": "pt_pt",
#     "LSA": "es",
#     "ARS": "hy",
#     "AUS": "en",
#     "OGS": "de",
#     "SBF": "fr",
#     "BVL": "es",
#     "LSB": "pt_br",
#     "BSL": "en",
#     "BLS": "bg",
#     "BRS": "fr",
#     "CBL": "km",
#     "CML": "fr",
#     "SCH": "es",
#     "CSL": "zh-CN",
#     "LSC": "es",
#     "CGS": "fr",
#     "SCR": "es",
#     "HZJ": "hr",
#     "CBS": "es",
#     "CSE": "cs",
#     "DSL": "da",
#     "NGT": "nl",
#     "SEC": "es",
#     "STD": "et",
#     "ESL": "am",
#     "FJS": "en",
#     "FSL": "en",
#     "FID": "fi",
#     "VGT": "nl",
#     "LSF": "fr",
#     "DGS": "de",
#     "GHS": "en",
#     "GSL": "el",
#     "LSG": "es",
#     "SHO": "es",
#     "HSL": "zh-TW",
#     "HDF": "hu",
#     "INS": "en",
#     "INI": "id",
#     "ISG": "en",
#     "QSL": "iw",
#     "ISL": "it",
#     "LSI": "fr",
#     "JML": "en",
#     "JSL": "ja",
#     "KSI": "en",
#     "KSL": "ko",
#     "LSL": "lv",
#     "LBS": "ar",
#     "LTS": "lt",
#     "TTM": "mg",
#     "MSL": "ny",
#     "BIM": "ms",
#     "MTS": "en",
#     "MNS": "en",
#     "LSM": "es",
#     "MSR": "mn",
#     "SLM": "pt_pt",
#     "BUS": "my",
#     "NSL": "ne",
#     "NZS": "en",
#     "LSN": "es",
#     "NNS": "en",
#     "NDF": "no",
#     "PSL": "es",
#     "LSP": "gn",
#     "SPE": "es",
#     "PDF": "pl",
#     "LGP": "pt_pt",
#     "LSQ": "fr",
#     "LMG": "ro",
#     "RSL": "ru",
#     "RWS": "rw",
#     "LSS": "es",
#     "SMS": "sm",
#     "SBS": "bs",
#     "SGL": "en",
#     "VSL": "sk",
#     "SZJ": "sl",
#     "SAS": "en",
#     "LSE": "es",
#     "SLS": "si",
#     "SSU": "nl",
#     "SSL": "sv",
#     "SGS": "de",
#     "TSL": "zh-TW",
#     "TZL": "sw",
#     "SIL": "th",
#     "TKL": "tr",
#     "USL": "en",
#     "LSU": "es",
#     "LSV": "es",
#     "SLV": "vi",
#     "ZAS": "en",
#     "ZSL": "en",
# }

def get_data_dir():
    # subfolder of the folder this script is in.
    # https://stackoverflow.com/questions/3430372/how-do-i-get-the-full-path-of-the-current-files-directory
    data_folder = Path(__file__).parent.resolve() 
    return data_folder

def load_dataset_file(filename):
    with gzip.open(filename, "rb") as f:
        loaded_object = pickle.load(f)
        return loaded_object

def get_sign_language_list():
    sign_spoken_json_path = get_data_dir() /"signlanguage_spokenlanguage.json"
    with open(str(sign_spoken_json_path), "r") as ssjf:
        signspoken = json.load(ssjf)
    return list(signspoken.keys())


def newindex_analysis_and_optionally_resave_as_json(resave_as_json=False):
    print("**************** NewIndex **********************")
    # https://stackoverflow.com/questions/3430372/how-do-i-get-the-full-path-of-the-current-files-directory
    
    newindex_path = get_data_dir() /"newindex.list.gz"
    newindex = load_dataset_file(str(newindex_path))

    newindex_keys = list(newindex[0].keys())

    print(f"KEYS: ")
    print(newindex_keys)

    print(f"VALUES:")
    verseIDs = list()
    verse_uniques = list()
    for item_dict in newindex[:10]:
        values = []
        for key in newindex_keys:
            values.append(item_dict[key])
        print(values)

    for item_dict in newindex:
        verseIDs.append(item_dict["verseID"])
        verse_uniques.append(item_dict["verse_unique"])

    print(f"There are {len(verseIDs)} listed verseIDs")
    print(f"There are {len(set(verseIDs))} unique verseIDs")


    print(f"There are {len(verseIDs)} listed verse_uniques")
    print(f"There are {len(set(verseIDs))} unique verse_uniques")

    
    jw_sign_df = pd.DataFrame.from_dict(newindex)
    jw_sign_df["verse_lang"] = pd.Categorical(jw_sign_df.verse_lang)
    print(jw_sign_df)
    # print(jw_sign_df.head())
    print(jw_sign_df.info())

    print(f"Counting video items per language and split")
    # load the splits. {"train": [verseIDs go here...], "dev": [precisely 1500 verse IDs], "test": [precisely 1500 verse IDs],}
    # load the splits. {"train": [verseIDs go here...], "dev": [precisely 1500 verse IDs], "test": [precisely 1500 verse IDs],}
    splits_path = get_data_dir().parent/"splits" /"jw_sign_splits.json"
    with open(str(splits_path), "r") as split_file:
        splits_dict = json.load(split_file)

    # load the names of all the sign languages
    sl_code_mappings_json_path =  get_data_dir()/"sign_language_code_mappings.json"
    with open(str(sl_code_mappings_json_path), "r") as slcmf:
        sign_language_code_mappings = json.load(slcmf)

    print(f"sign_language,english_name,item_count, train/dev/test")

    for sign_language in get_sign_language_list():
        video_data_items_for_this_lang = [
            datum for datum in newindex if datum["verse_lang"] == sign_language
        ]

        video_data_df = pd.DataFrame.from_dict(video_data_items_for_this_lang)
        # print(video_data_df)

        if video_data_df.empty:
            print(
                f"{sign_language}, NO DATA, {len(video_data_items_for_this_lang)}, ?/?/?"
            )
        else:
            train_video_data_df = video_data_df[
                video_data_df["verseID"].isin(splits_dict["train"])
            ]
            dev_video_data_df = video_data_df[
                video_data_df["verseID"].isin(splits_dict["dev"])
            ]
            test_video_data_df = video_data_df[
                video_data_df["verseID"].isin(splits_dict["test"])
            ]
            print(
                f"{sign_language}, {sign_language_code_mappings[sign_language]['english_name']}, {len(video_data_items_for_this_lang)}, {train_video_data_df.shape[0]}/{dev_video_data_df.shape[0]}/{test_video_data_df.shape[0]}"
            )

    # print(f"{split}, {split_video_data_df.shape[0]}")  # get the number of rows

    if resave_as_json:

        out_path = get_data_dir()/"jw_sign.json"
        with open(str(out_path), "w") as jf:
            # TODO: save more efficiently
            # https://towardsdatascience.com/the-best-format-to-save-pandas-data-414dca023e0d
            json.dump(newindex, jf)

    print("\nSHUFFLING\n")
    print(newindex_keys)
    random.shuffle(newindex)
    for item_dict in newindex[:10]:
        values = []
        for key in newindex_keys:
            values.append(item_dict[key])
        print(values)


def sign_spoken_json_analysis():
    print("**************** signlanguage_spokenlanguage.json **********************")
    sign_langs = []

    spoken_langs = []
    print("|Sign Language\t|Spoken Language| spoken language (BCP-47 via langcodes)\t|")
    print("|-----|--------|-------------|-----------|")

    sign_spoken_path = get_data_dir() / "signlanguage_spokenlanguage.json"
    with open(str(sign_spoken_path), "r") as ssjf:
        signspoken = json.load(ssjf)

        for sign_lang, spoken_lang in signspoken.items():
            standardized_tag = langcodes.standardize_tag(spoken_lang)
            print(
                "|",
                sign_lang,
                "|",
                spoken_lang,
                "|",
                standardized_tag,
                "|",
            )
            sign_langs.append(sign_lang)
            spoken_langs.append(spoken_lang)
            print(signspoken)

    print(f"There are {len(set(sign_langs))} sign languages")
    print(f"There are {len(set(spoken_langs))} spoken languages")


def open_language_code_mappings_csv_and_save_to_json():
    codes_explained_path = get_data_dir()/"sign_language_codes_explained.csv"
    sign_language_codes_explained_df = pd.read_csv(
        str(codes_explained_path)
    )
    print(sign_language_codes_explained_df)

    sign_language_code_mappings = {}

    for _, row in sign_language_codes_explained_df.iterrows():
        mappings_for_this_acronym = {}
        mappings_for_this_acronym["sign_sil_initial"] = row["sign_sil_initial"]
        mappings_for_this_acronym["english_name"] = row["english_name"]
        sign_language_code_mappings[row["common_acronym"]] = mappings_for_this_acronym

    sign_language_code_mappings_json_out_path = get_data_dir()/"sign_language_code_mappings.json"
    with open(str(sign_language_code_mappings_json_out_path), "w") as jf:
        json.dump(sign_language_code_mappings, jf)


def text51_dict_analysis():
    text51_path = get_data_dir()/"text51.dict.gz"
    text51_dict = load_dataset_file(str(text51_path))
    print("************** TEXT51 ************************")
    print(text51_dict.keys())
    print("|Tag\t|BCP-47\t|Language name|verse count|")
    print("|-----|--------|-------------|-----------|")
    print
    for lang_tag in text51_dict.keys():
        standardized_tag = langcodes.standardize_tag(lang_tag)
        langcode_object = langcodes.get(lang_tag)
        # print("**********************************************")
        print(
            f"|{lang_tag:5s}\t|{standardized_tag:5s}\t|{langcode_object.display_name():24s}\t|{len(text51_dict[lang_tag].keys())}|"
        )
        data_item_keys = list(text51_dict[lang_tag].keys())
        # for data_index, data_item_key in enumerate(data_item_keys[:10]):
        #     data_item = text51_dict[lang][data_item_key]
        #     print(f"lang: {lang} {data_index}. Key: {data_item_key}")
        #     print(data_item)

        # print("**********************************************")

    # print(len(text51_dict['ru'].keys()))
    # with open("text51.json", "w") as jf:

    #     json.dump(text51_dict, jf)


def split_file_analysis_and_resave_as_json():
    # https://drive.google.com/file/d/1DgfnPV0-KTXCAivQDrrOHLOaAqQ-zx2L/view?usp=drive_link
    splits_path = get_data_dir()/ "splits.dict"
    splits_dict = load_dataset_file(str(splits_path))
    print()
    print()
    print(f"Splits: {splits_dict.keys()}")

    for key, value in splits_dict.items():
        print(f"Split {key}: {len(value)} items")
        print(f"10 random values:")
        print(random.sample(value, 10))

    splits_dict_renamed = dict()
    splits_dict_renamed["train"] = splits_dict["train_ids"]
    splits_dict_renamed["dev"] = splits_dict["dev_ids"]
    splits_dict_renamed["test"] = splits_dict["test_ids"]

    with open("jw_sign_splits.json", "w") as jf:
        json.dump(splits_dict_renamed, jf)


def combine_videos_and_verses(sign_language="ALS"):
    """
    OK so you want <sign_language>?
    Let me go collect the spoken-language verse texts and sign-language video URLs that correspond to that.
    """

    # get the sign to spoken mappings
    sign_spoken_path = get_data_dir() / "signlanguage_spokenlanguage.json"
    with open(str(sign_spoken_path), "r") as ssjf:
        signspoken = json.load(ssjf)

    spoken_language = signspoken[sign_language]
    print(
        f"OK, the corresponding spoken language for {sign_language} in this dataset is {spoken_language}"
    )

    # load the verse texts. Ordered by spoken-language text. Example: text51["ja"]["v1001001"]
    print(f"Retrieving spoken-language texts for {spoken_language}")
    text51_dict = load_dataset_file("data/text51.dict.gz")
    verses_for_corresponding_spoken_lang = text51_dict[spoken_language]
    print(f"{len(verses_for_corresponding_spoken_lang)} verses retrieved")
    print(f"{type(verses_for_corresponding_spoken_lang)}")  # dict of verseIDs
    # spoken_language_verses_df = pd.DataFrame(spoken_language_verses)
    # print(spoken_language_verses_df)

    # Get the URLS to videos, as well as which verses they correspond to
    # A pickled Python list with URL links to the videos.
    # Each list item is a dictionary.
    # As far as I can tell,
    # Keys: ['video_url', 'video_name', 'verse_lang', 'verse_name', 'verse_start', 'verse_end', 'duration', 'verse_unique', 'verseID']
    print(f"Retrieving video information: ")
    newindex_path = get_data_dir()/"newindex.list.gz"
    jw_sign_url_index_dict = load_dataset_file(str(newindex_path))

    video_data_items = list()
    for datum in jw_sign_url_index_dict:
        if datum["verse_lang"] == sign_language:
            video_data_items.append(datum)

    print(f"{len(video_data_items)} video data items retrieved")
    print(video_data_items[0])

    video_data_df = pd.DataFrame.from_dict(video_data_items)
    print(video_data_df)

    ################################################################
    # Associate on verse_id
    # print(video_data_df["verseID"])
    print()
    # video_data_df.query('verseID == "v2001001"')
    print(video_data_df.query('verseID == "v2001001"'))
    print(verses_for_corresponding_spoken_lang["v2001001"])
    # video_data_df["verse"] = verses_for_corresponding_spoken_lang
    # print(video_data_df.query('verseID == "v2001001"'))
    # print(video_data_df)

    # convert to dataframe attempt 1
    # https://stackoverflow.com/questions/57631895/dictionary-to-dataframe-error-if-using-all-scalar-values-you-must-pass-an-ind
    # verses_for_corresponding_spoken_lang_df = pd.DataFrame(
    #     [verses_for_corresponding_spoken_lang]
    # )
    # print(
    #     verses_for_corresponding_spoken_lang_df
    # )  # shaped something like 1 rows x 31078 column

    # https://stackoverflow.com/a/29794993
    # Call map and pass the dict, this will perform a lookup and return the associated value for that key:
    print("MAPPING")
    video_data_df["verse"] = video_data_df["verseID"].map(
        verses_for_corresponding_spoken_lang
    )
    video_data_df = video_data_df.drop(
        columns=["video_name", "verse_lang", "verse_name"]
    )
    print(video_data_df)
    print(video_data_df.info())

    # https://stackoverflow.com/questions/29794959/pandas-add-new-column-to-dataframe-from-dictionary

    ########################################################################

    # load the splits. {"train": [verseIDs go here...], "dev": [precisely 1500 verse IDs], "test": [precisely 1500 verse IDs],}
    splits_path = get_data_dir().parent/"splits" /"jw_sign_splits.json"
    with open(str(splits_path), "r") as split_file:
        splits_dict = json.load(split_file)

    print(f"Assigning video data for {sign_language} to splits")
    print(f"split, item_count")

    for split in splits_dict.keys():
        # print()
        # print(f"gathering video data for {split} split")
        split_video_data_df = video_data_df[
            video_data_df["verseID"].isin(splits_dict[split])
        ]
        print(f"{split}, {split_video_data_df.shape[0]}")  # get the number of rows


if __name__ == "__main__":
    # text51_dict_analysis()

    newindex_analysis_and_optionally_resave_as_json()

    # sign_spoken_json_analysis()

    # split_file_analysis()

    # split_path = Path.cwd() / "splits" / "jw_sign_splits.json"
    # with open(str(split_path)) as jf:
    #     splits_from_json = json.load(jf)
    # # print(splits_from_json)
    # for split_name, split_verses in splits_from_json.items():
    #     print(split_name)
    #     print(len(split_verses))

    

    # combine_videos_and_verses(random.choice(list(signspoken.keys())))
    # combine_videos_and_verses("ASL")

    # open_language_code_mappings_csv_and_save_to_json()
