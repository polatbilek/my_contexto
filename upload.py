import json
from typing import Dict, List, Optional
import random
from datetime import datetime, timedelta

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import Transaction
import gensim.downloader

creds = credentials.Certificate("words-82737-firebase-adminsdk-bknzb-a18dc253d6.json")
app = firebase_admin.initialize_app(creds)
store = firestore.client(app)
full_vocabulary_file_name = "clean_30k.json"
random_words_vocabulary_file_name = "random_playing_words.json"


def get_daily_doc_name(date: datetime) -> str:
    return f"{date.year}.{date.month:02d}.{date.day:02d}"


def upload_to_firestore(target_word: str, similarities: Dict[str, str], collection_name: str, date: Optional[datetime] = None, top_limit: int = 1000, tx: Optional[Transaction] = None):
    doc_name = get_daily_doc_name(date) if date is not None else target_word
    doc_ref = store.collection(collection_name).document(doc_name)
    data = {
        "exactWord": target_word,
        "words": list(similarities.keys())[:top_limit],
    }
    tx.set(doc_ref, data) if tx is not None else doc_ref.set(data)


def get_similarity_for_vocab(target_word: str, vocabulary: List[str], precision: int = 7) -> Dict[str, str]:
    word_similarities = {}
    glove_vectors = gensim.downloader.load('glove-twitter-200')

    for word in vocabulary:
        if word != target_word:
            try:
                word_similarities[word] = glove_vectors.similarity(target_word, word)
            except KeyError:
                # print(f"Couldn't find this word in model: {word}")
                pass

    return {k: str(round(v, precision)) for k, v in sorted(word_similarities.items(), key=lambda x: x[1], reverse=True)}


def get_vocabulary(filename: str) -> List[str]:
    word_dict = json.load(open(filename, "r"))
    return list(word_dict.keys())


def get_random_word(word_list: List[str]) -> str:
    return random.choice(word_list)


def update_similarity_based_on_date(start_date: datetime, end_date: datetime, replace_existing: bool = True, update_all_random_words: bool = False, update_new_random_words: bool = False):
    """
    Updates the similarity scores for the daily game and random words similarities for paid user's game.

    :param start_date: (datetime) start date, this date is included
    :param end_date: (datetime) end date, this date is included
    :param replace_existing: (bool) Replaces existing words on that day if found in firestore
    :param update_all_random_words: (bool) Updates random words' similarities for paid users' words.
        If found in firestore, replace existing. Any found document on firestore but not found in json will be deleted.
    :param update_new_random_words: (bool) Just looks if there is a new random word found in json but not in firestore, then updates it.
    :return: Doesn't return anything
    """
    if update_all_random_words and update_new_random_words:
        raise ValueError("Both update_all_random_words and update_new_random_words cannot be True at the same time")

    target_date = start_date
    vocab = get_vocabulary(full_vocabulary_file_name)

    while target_date < end_date:
        update = True
        target_word = None
        doc = store.collection("daily").document(get_daily_doc_name(target_date)).get()

        if doc.exists:
            if not replace_existing:
                update = False  # Because we didn't want to replace existing day, if exists pass that day
            else:
                target_word = doc.to_dict()["exactWord"]
        else:
            target_word = get_random_word(vocab)

        if update:
            similarity_dict = get_similarity_for_vocab(target_word, vocab)
            upload_to_firestore(target_word, similarity_dict, "daily", target_date)

        target_date = target_date + timedelta(days=1)

    if update_all_random_words:
        random_words = list(get_vocabulary(random_words_vocabulary_file_name))
        print(random_words)
        all_words_in_firestore = store.collection("randomPlays").document("allWords").get().to_dict()
        new_all_words_in_firestore: List[str] = all_words_in_firestore["words"].copy()

        for firestore_word in all_words_in_firestore["words"]:
            if firestore_word in random_words:
                random_words.remove(firestore_word)
                if update_all_random_words:
                    print("1 ", firestore_word, datetime.now())
                    similarity_dict = get_similarity_for_vocab(firestore_word, vocab)
                    print("2 ", datetime.now())
                    upload_to_firestore(firestore_word, similarity_dict, "randomPlays")
                    print("3 ", datetime.now())

            elif update_all_random_words:
                new_all_words_in_firestore.remove(firestore_word)
                tx = store.transaction()
                tx.delete(store.collection("randomPlays").document(firestore_word))
                tx.set(store.collection("randomPlays").document("allWords"), {"words": new_all_words_in_firestore}, merge=False)
                tx.commit()

        if len(random_words) > 0:
            print(f"There are {len(random_words)} new words to add to firestore for random play word set")
            for target_word in random_words:
                similarity_dict = get_similarity_for_vocab(target_word, vocab)
                new_all_words_in_firestore.append(target_word)
                tx = store.transaction()
                upload_to_firestore(target_word, similarity_dict, "randomPlays", tx=tx)
                tx.set(store.collection("randomPlays").document("allWords"), {"words": new_all_words_in_firestore}, merge=False)
                tx.commit()


if __name__ == '__main__':
    start = datetime(year=2026, month=3, day=29)
    end = datetime(year=2026, month=4, day=2)

    update_similarity_based_on_date(start, end, replace_existing=False, update_all_random_words=True)
