# Instruction
- Create virtual environment with Python 3.7
```
$ py -3.7 -m venv env
```
- Activate virtual environment
- Install required libraries
```
$ pip install -r requirements.txt
```
- Open `config.json`. Ensure that `input_folder_path` is `practicedata` and `output_model_path` to `practicemodels`.
- Run the following commands one by one
```
$ setup.sh
```
```
$ python -m scripts.apicalls
```
- Enter the `config.json` file. Change `input_folder_path` to `sourcedata` and `output_model_path` to `models`.
- Run the full process
```
$ python -m scripts.fullprocess
```
- Set up the cron job
```
$ python automate.py add-cron-job
```
- Hack away! 🔨🔨