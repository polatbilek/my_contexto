import json
from typing import Dict, List, Tuple
import random
from datetime import datetime

import firebase_admin
import google.cloud
from firebase_admin import credentials, firestore
import gensim.downloader


def upload_to_firestore(target_word: str, similarities: Dict[str, str], date: datetime):
    store = firestore.client(firebase_admin.initialize_app(credentials.Certificate("words-82737-firebase-adminsdk-bknzb-a18dc253d6.json")))

    doc_ref = store.collection("daily").document(f"{date.year}.{date.month:02d}.{date.day:02d}")
    doc_ref.set({
        "exactWord": target_word,
        "words": list(similarities.keys()),
    })


def get_similarity_for_vocab(target_word: str, vocabulary: List[str]) -> Dict[str, str]:
    word_similarities = {}
    glove_vectors = gensim.downloader.load('glove-twitter-200')

    for word in vocabulary:
        if word != target_word:
            try:
                word_similarities[word] = glove_vectors.similarity(target_word, word)
            except KeyError:
                pass

    return {k: str(round(v, 7)) for k, v in sorted(word_similarities.items(), key=lambda x: x[1], reverse=True)}


def get_vocabulary(filename: str) -> List[str]:
    word_dict = json.load(open(filename, "r"))
    return list(word_dict.keys())


def get_random_word(word_list: List[str]) -> str:
    return random.choice(word_list)


if __name__ == '__main__':
    for_date = datetime(year=2025, month=1, day=1)
    vocabulary_file_name = "clean_30k.json"

    vocab = get_vocabulary(vocabulary_file_name)
    target = get_random_word(vocab)
    similarity_dict = get_similarity_for_vocab(target, vocab)
    upload_to_firestore(target, similarity_dict, for_date)
