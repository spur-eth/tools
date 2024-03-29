import argparse
import pathlib
import sys
from tqdm import tqdm
import chardet
import pandas as pd

from dotenv import load_dotenv
import os
import deepl


def translate(input_txt_path, output_folder, source_lang, target_lang):
    """Use DeepL API to translate an input_txt_path and write to output_folder.

    Gets contents from a text file and uses DeepL API to translate them to output language (target_lang)
    and puts a translated output file into the output folder. If source_lang is specified, the DeepL API is called
    with that input for the source language and otherwise it attempts to detect the source language. The default
    target language is American English, but that can be altered by modifying the target_lang variable.
    """
    source_lang_text = read_file_contents(input_txt_path)
    if source_lang == "":
        source_info, translated_text = call_deepl_detect_source_lang(
            source_lang_text, target_lang
        )
    else:
        source_info, translated_text = call_deepl(
            source_lang_text, source_lang, target_lang
        )
    output_path = construct_output_path(
        output_folder, input_txt_path, source_info, target_lang
    )
    write_to_file(output_path, translated_text)


def run_translate(input_txt_path, output_folder, source_lang, target_lang):
    """Determines if the user is calling the translator for a txt file or a folder of them and runs the translation iteratively if needed"""
    input_info = pathlib.Path(input_txt_path)
    if input_info.is_dir():
        translated_file_count = 0
        for item in tqdm(input_info.iterdir()):
            if (item.is_file()) and (".txt" in str(item)):
                translate(str(item), output_folder, source_lang, target_lang)
                translated_file_count += 1
        print(
            f"Your files are ready! {translated_file_count} files translated. Thanks for using this tool and have a nice day :D "
        )
        return
    if (input_info.is_file()) and (".txt" in input_txt_path):
        translate(input_txt_path, output_folder, source_lang, target_lang)
        print("Your file is ready! Thanks for using this tool and have a nice day :D ")
    else:
        print()
        print(
            f"The file you have selected is not a .txt file, please check the {input_txt_path}"
        )


def read_file_contents(file_path):
    with open(file_path, "r") as file:
        contents = file.read()
    return contents


def call_deepl(source_lang_text, source_lang, target_lang):
    auth_key = os.getenv("DEEPL_API_KEY")
    translator = deepl.Translator(auth_key)
    result = translator.translate_text(
        source_lang_text, source_lang=source_lang, target_lang=target_lang
    )
    source_info = "manual_" + source_lang
    translated_text = result.text
    return source_info, translated_text


def call_deepl_detect_source_lang(source_lang_text, target_lang):
    auth_key = os.getenv("DEEPL_API_KEY")
    translator = deepl.Translator(auth_key)
    result = translator.translate_text(source_lang_text, target_lang=target_lang)
    detected_source_lang = result.detected_source_lang
    source_info = "auto_" + detected_source_lang
    translated_text = result.text
    return source_info, translated_text


def construct_output_path(
    output_folder: str, input_file_path: str, source_info: str, target_lang: str
):
    file_name = os.path.basename(input_file_path)
    file_name_no_ext = os.path.splitext(file_name)[0]
    if ".txt" in str(file_name):
        output_file_name = f"{file_name_no_ext}_{source_info}_{target_lang}.txt"
    if ".csv" in str(file_name):
        output_file_name = f"{file_name_no_ext}_{source_info}_{target_lang}.csv"
    return os.path.join(output_folder, output_file_name)


def write_to_file(file_path, contents):
    with open(file_path, "w") as file:
        file.write(contents)


def get_file_encoding(file_path: str):
    """Because different file encodings that can give rise to errors, we will read in a small part of the file to detect the encoding with chardet to pass to the reader."""
    with open(file_path, "rb") as f:
        raw_data = f.read(1024)  # Read the first 1024 bytes of the file
        encoding = chardet.detect(raw_data)["encoding"]
        return encoding


def read_csv_file_contents(file_path: str, id_col: str, text_cols: list):
    """Reads data from a .csv or .txt file with tabular data where each row contains a unique identifier columns (id_col) and open text fields (text_cols).
    (This could correspond to survey respondents' answers.) After determining the encoding, the function returns a dataframe of the users and the
    open text columns to be translated."""
    encoding = get_file_encoding(file_path)
    cols = [id_col] + text_cols
    try:
        open_responses = pd.read_csv(file_path, encoding=encoding, sep=",")
    except pd.errors.ParserError:
        open_responses = pd.read_csv(file_path, encoding=encoding, sep="\t")
    open_responses = open_responses[cols]
    return encoding, open_responses


def run_translate_csv(
    input_file_path: str,
    id_col: str,
    text_cols: list,
    source_lang: str,
    target_lang: str,
    output_folder: str,
):
    """Determines if the user is calling the translator for a csv file or a folder containing several of them and runs the program iteratively if needed"""
    input_info = pathlib.Path(input_file_path)
    if input_info.is_dir():
        translated_file_count = 0
        for item in tqdm(input_info.iterdir()):
            if (item.is_file()) and (".csv" in str(item)):
                translate_csv(
                    str(item),
                    id_col,
                    text_cols,
                    source_lang,
                    target_lang,
                    output_folder,
                )
                translated_file_count += 1
        print(
            f"Your files are ready! {translated_file_count} files translated. Thanks for using this tool and have a nice day :D "
        )
        return
    if (input_info.is_file()) and (".csv" in input_file_path):
        translate_csv(
            str(input_info), id_col, text_cols, source_lang, target_lang, output_folder
        )
        print("Your file is ready! Thanks for using this tool and have a nice day :D ")
    else:
        print(
            "The file you have selected is not a .csv file, please check the input_file_path"
        )


def translate_csv(
    input_file: str,
    id_col: str,
    text_cols: list,
    source_lang: str,
    target_lang: str,
    output_folder: str,
):
    """Use DeepL API to translate an csv with tabular data with rows correponding to entries (e.g. respondents) and columns with text to translate and append a translated version of each entry for each column to a new .csv and write to an output_folder.

    Applies the DeepL translation across text columns (text_cols) within a dataframe as from read_csv_file_contents() and writes a text file with a dataframe with columns for the ids (id_col), the original texts and translated texts (with the same encoding as the input file).
    Gets contents from a csv file and loads into a dataframe and uses DeepL API to translate the text in columns with text to output language (target_lang) and appends the translated text for each column to the dataframe and writes out the dataframe as a new csv file into the output folder.
    If source_lang is specified, the DeepL API is called with that input for the source language and otherwise it attempts to detect the source language. The default target language is American English, but that can be altered by modifying the target_lang variable.
    """
    # file_name_no_ext = get_filename(input_file)
    encoding, df = read_csv_file_contents(input_file, id_col, text_cols)

    if source_lang == "":
        detected_source_lang = call_deepl_detect_source_lang(
            str(df[text_cols].iloc[0]), target_lang
        )[0]
        translated_cols = df[text_cols].applymap(
            lambda x: call_deepl_detect_source_lang(str(x), target_lang)[1]
        )
        source_lang = detected_source_lang
    else:
        translated_cols = df[text_cols].applymap(
            lambda x: call_deepl(str(x), source_lang, target_lang)[1]
        )
    df_w_translation = df.merge(
        translated_cols,
        left_index=True,
        right_index=True,
        suffixes=["", f"_translated_{target_lang}"],
    )
    output_path = construct_output_path(
        output_folder, input_file, source_lang, target_lang
    )
    df_w_translation.to_csv(output_path, encoding=encoding, sep="\t")


def main():
    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_folder",
        help="Specify folder with text files to translate",
        required=True,
    )
    parser.add_argument(
        "--output_folder",
        help="Specify folder for the translated text files",
        required=True,
    )
    parser.add_argument(
        "--source_lang", help="Specify original text language", default=""
    )
    parser.add_argument(
        "--target_lang", help="Specify target text language", default="EN-US"
    )
    parser.add_argument(
        "--is_csv",
        help="Specify whether input is in csv format",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--id_col_csv", help="Specify id column name in csv", default=""
    )

    parser.add_argument(
        "--text_cols_csv", help="Specify id column name in csv", default="", nargs="+"
    )

    args = parser.parse_args()

    if args.is_csv:
        print("The text columns are:", args.text_cols_csv)
        run_translate_csv(
            args.input_folder,
            args.id_col_csv,
            args.text_cols_csv,
            args.source_lang,
            args.target_lang,
            args.output_folder,
        )
    else:
        run_translate(
            args.input_folder, args.output_folder, args.source_lang, args.target_lang
        )


if __name__ == "__main__":
    sys.exit(main())
