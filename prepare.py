import nltk
import json
from nltk.corpus import stopwords

nltk.download('stopwords')


def clean_words(file_name: str = "30k.txt", cleaned_file_name: str = "clean_30k.json"):
    stop_words = set(stopwords.words('english'))
    word_dict = {}

    with open(file_name, "r") as f:
        with open(cleaned_file_name, "a+") as w:
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
