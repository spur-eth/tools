# Tool for automatically translating text files with DeepL using the DeepL API

## Setup 
1) Get DeepL API Key\
  At the following site, sign up for a DeepL plan to recieve an API Key: [DeepL API](https://www.deepl.com/docs-api)

    > "You can access the DeepL API with either a DeepL API Free or DeepL API Pro plan.
    > With the DeepL API Free plan, you can translate up to 500,000 characters per month for free. For more advanced use cases, the DeepL API Pro plan allows unlimited translation with usage-based pricing, maximum data security, and prioritized execution of translation requests."

2) Create environment (requires [conda](https://docs.conda.io/en/latest/)) 

    ```shell
    conda create --name translator python=3.9
    pip install -r deepl/code/requirements.txt
    ```

   Make an .env file with the following variable to store and use your DeepL API key safely: 
    ```shell
    echo "DEEPL_API_KEY=<copy key here>" > deepl/code/.env
    ```


## Run
Run a command like the following to use the tool to translate a folder of text files to be translated or on an individual text file: 

The following command will autodetect the languages of the text documents in the INPUT_FOLDER and translate them to American English and put the translated documents (with their detected langauge and the target language added to the file names) into the OUTPUT_FOLDER: 
```
INPUT_FOLDER=<paste here>
OUTPUT_FOLDER=<paste here>

python code/translator.py \
    --input_folder=${INPUT_FOLDER} \
    --output_folder=${OUTPUT_FOLDER}
```

To adjust the target language or manually specify the source langauge, add the SOURCE_LANG and TARGET_LANG variables. The following command will translate the specified French text document(s) in the INPUT_FOLDER and translate them to German and put the translated document(s) (with their detected langauge and the target language added to the file names) into the OUTPUT_FOLDER: 

```
INPUT_FOLDER=<paste here>
OUTPUT_FOLDER=<paste here>
SOURCE_LANG=FR
TARGET_LANG=DE

python code/translator.py \
    --input_folder=${INPUT_FOLDER} \
    --output_folder=${OUTPUT_FOLDER} \
    --source_lang=${SOURCE_LANG} \
    --target_lang=${TARGET_LANG}
```

For running with tabular data, for instance csv files where each row are correspondent answers and some columns represent text responses in another language we can export a csv file with the respondent ids and the text responses and their desired translations by setting the --is_csv flag to tell the progam to do this and specifying what column you want to use as the id column to map the responses back to the respondents and the columns with text to translate. Note that if there is more than one column with text, the text columns must be passed as with spaces in between and it is easiest to pass them into the command directly. 

For example if we have one or more surveys in .csv format in our input folder with respondent identifiers in the 'ID' column and we want to autodetect the language for each text entry in each text column (text_col1, text_col2, and textcol3) and translate it to the default (American English) and write the results to an output folder for all the surveys we could use the following command formatting: 

```
INPUT_FOLDER=<paste here>
OUTPUT_FOLDER=<paste here>
ID_COL='ID'


python code/translator.py \
    --input_folder=${INPUT_FOLDER} \
    --output_folder=${OUTPUT_FOLDER} \
    --source_lang=${SOURCE_LANG} \
    --target_lang=${TARGET_LANG} \
    --is_csv \
    --id_col_csv=${ID_COL} \
    --text_cols_csv text_col1 text_col2 text_col3
```

### Other resources 

- (To use the languages supported by DeepL and how they are referred to go to [this page](https://www.deepl.com/docs-api/translate-text/translate-text/) and search 'source_lang')

- More useful information for navigating the API: [DeepL API Python Integration](https://www.deepl.com/en/blog/announcing-python-client-library-for-deepl-api)