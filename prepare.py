import nltk
import json
import ssl

from nltk.corpus import stopwords

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


#nltk.download("stopwords")  # Open this if you haven't downloaded yet, after downloading first time, you can comment it back.


def clean_words(file_name: str = "30k.txt", cleaned_file_name: str = "clean_30k.json"):
    stop_words = set(stopwords.words('english'))
    word_dict = {}

    with open(file_name, "r") as f:
        with open(cleaned_file_name, "w") as w:
            for line in f:
                word = line.strip()

                if word not in stop_words and len(word) > 2:
                    if (word.endswith("s") and word[:-1] in word_dict) or word + "s" in word_dict:
                        pass
                    else:
                        word_dict[word] = 1

            json.dump(word_dict, w, indent=4)


if __name__ == "__main__":
    clean_words()
