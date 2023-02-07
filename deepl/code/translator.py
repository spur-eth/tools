import argparse
import pathlib
import sys
from tqdm import tqdm
from dotenv import load_dotenv
import os
import deepl


def translate(input_txt_path, output_folder, source_lang, target_lang):
    """Use DeepL API to translate an input_txt_path and write to output_folder.

    Gets contents from a text file and uses DeepL API to translate them to output language (target_lang) and puts a translated output file into the output folder. If source_lang is specified, the DeepL API is called with that input for the source language and otherwise it attempts to detect the source language. The default target language is American English, but that can be altered by modifying the target_lang variable.
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
    """Determines if the user is calling the translator for a file or a folder and runs it iteratively if needed"""
    input_info = pathlib.Path(input_txt_path)
    if input_info.is_dir():
        translated_file_count = 0
        for item in tqdm(input_info.iterdir()): 
            if (item.is_file()) and ('.txt' in str(item)):
                translate(str(item), output_folder, source_lang, target_lang)
                translated_file_count += 1
        print(f"Your files are ready! {translated_file_count} files translated. Thanks for using this tool and have a nice day :D ")
        return
    else:   
        if (input_info.is_file()) and ('.txt' in input_txt_path):
            translate(input_txt_path, output_folder, source_lang, target_lang)
            print("Your file is ready! Thanks for using this tool and have a nice day :D ")
        else: 
            print("The file you have selected is not a .txt file, please check the input_txt_path")
            pass
        return
    

def read_file_contents(file_path):
    with open(file_path, "r") as file:
        contents = file.read()
    return contents

def call_deepl(source_lang_text, source_lang, target_lang):
    auth_key = os.getenv('DEEPL_API_KEY')
    translator = deepl.Translator(auth_key)
    result = translator.translate_text(
        source_lang_text, source_lang=source_lang, target_lang=target_lang
        )
    source_info = 'manual_' + source_lang
    translated_text = result.text
    return source_info, translated_text

def call_deepl_detect_source_lang(source_lang_text, target_lang):
    auth_key = os.getenv('DEEPL_API_KEY')
    translator = deepl.Translator(auth_key)
    result = translator.translate_text(
        source_lang_text, target_lang=target_lang
        )
    detected_source_lang = result.detected_source_lang
    source_info = 'auto_' + detected_source_lang
    translated_text = result.text
    return source_info, translated_text


def construct_output_path(
    output_folder, input_txt_path, source_info, target_lang
):
    file_name = os.path.basename(input_txt_path)
    file_name_no_ext = os.path.splitext(file_name)[0]
    output_file_name = (
        f"{file_name_no_ext}_{source_info}_{target_lang}.txt"
    )
    return os.path.join(output_folder, output_file_name)


def write_to_file(file_path, contents):
    with open(file_path, "w") as file:
        file.write(contents)


def main():
    load_dotenv()
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_folder", help="Specify folder with text files to translate", required=True)
    parser.add_argument("--output_folder", help="Specify folder for the translated text files", required=True)
    parser.add_argument("--source_lang", help="Specify original text language", default="")
    parser.add_argument("--target_lang", help="Specify target text language", default="EN-US")
    args = parser.parse_args()

    run_translate(args.input_folder, args.output_folder, args.source_lang, args.target_lang)

if __name__ == "__main__":
    sys.exit(main())
    
