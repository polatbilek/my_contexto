# Contexto Word Creator

This project uses given words in a vocabulary file (e.g. 30k.txt), cleans it with `prepare.py` to create `clean_30k.json` and uploads to 
firestore in a prepared way via `upload.py`.

### Requirements
- Project works on python3.11. You better check if you already have python3.11 installed via commands explained here. If you dont have, you can download it via this link. https://www.python.org/downloads/release/python-3119/ . While installing you
can choose "add to path" tick, that makes your life easier. This installation adds `python` or `python3` or `python3.11` command to your terminal.
 You can check it via `python -V` command. It will print out the version. Which of these commands has 3.11 is the one you should use. (It may require PC restart after install)
- For python you don't need any IDE. If you want it is better to install VSCode since it is very lightweight. You can configure 
python installation to your VSCode and run with IDE or you can use VSCode as an editor and run your script via terminal.
- After you install python, you should already have `pip` command. `pip` is python package manager command. You can use it in terminal as well.
If you dont have pip coming with your python installation. You can use this link to install https://pip.pypa.io/en/stable/installation/
pip will be installed either `pip` or `pip3` you can try either of them. Enter command `pip -V` or `pip3 -V` to see your
pip's python version. It should be 3.11.
- You need to drag and drop your firebase credentials json file to the folder. It is already in gitignore so it will not 
pushed into git repo and noone will see it. Its default name is `words-82737-firebase-adminsdk-bknzb-a18dc253d6.json`. If you want to use
different credentials or different file name make sure to add it to .gitignore file and change credentials filename in `upload.py`


### Installation & Run
The commands `python` might change for `python3` or `python3.11` due to your system. Same with `pip` as well. And please don't run directly each command. 
First read it why it is there how it can be used, then run it.

- Clone the git repo, open a terminal and navigate to that folder.
- Run `pip install -r requirements.txt` command in your terminal. This will download all needed packages. It might take a while.
- If you want to change your vocabulary, add more or do some transformations etc. Run `python prepare.py` for preparation of clean_30k.json.
But there is already one clean json uploaded. So at start you won't need that command.
- You can run `python upload.py` to upload similar word list to your firebase. However, it needs adjustments of time and commands. At below of `upload.py` 
you can see `if __name__ == '__main__':` part. That part is main. `start` and `end` variable determine which date intervals you want to create and upload. 
It calls `update_similarity_based_on_date` method which basically does all the job. When you executed the command it will start downloading word models. So that 
is no problem, wait for its download, after that it will start to run. 1 Run for 1 day takes 3 4 minutes, so wait for it. `update_similarity_based_on_date` 
has arguments of start and end datetimes which is explained above. Also it has `replace_existing` argument which means in given date interval if it founds document in firestore
it will not update it if you provide it `False`, updates it if your provide `True`. `update_all_random_words` updates random words' similarities for paid users' words.
If found in firestore, replace existing. Any found document on firestore but not found in json will be deleted. So basically it syncs your `random_playing_words.json` with firestore exactly.
`update_new_random_words` just looks if there is a new random word found in `random_playing_words.json` but not in firestore, then updates it. 
- To add new words you can either add it to 30k.txt and run prepare.py or you can directly add it to clean_30k.json with obeying its format. 
If you add it directly to clean_30k.json, the first run of prepare.py will delete that word since prepare.py looks at 30k.txt and deleted content of clean_30k.json and write into it.
If you add it to 30k.txt and run prepare.py be careful about which word you added. We clean stopwords and words with plurals (there is either "pencil" in word list or "pencils" not both).
So your added word might be cleaned up and not shown in clean_30k.json. Just check it after prepare.py execution.
- If you want to update arbitrary dates (like between 05.12.2024-10.12.2024 and 20.12.2024-25.12.2024) you can call update_similarity_based_on_date 2 times
inside `if __name__ == '__main__':` with same parameters but different time ranges.