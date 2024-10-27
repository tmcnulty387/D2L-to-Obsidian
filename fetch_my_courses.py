import requests, re, os, configparser, ast
from ics import Calendar
from datetime import datetime, timezone


config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'env', 'config.ini')
config = configparser.ConfigParser()
config.read(config_path)
url = config['settings']['url']
path = config['settings']['path']
word_limit = config['settings']['word_limit']
exclude_strings = config['settings']['exclude_strings']

tz: timezone = timezone.utc
after: datetime = datetime.now(tz)
before: datetime = datetime.max.replace(tzinfo=tz)

def format_string(input_str, max_words=-1, cutoff_str=None, remove_brackets=True):

    input_str = input_str.strip()

    # removes any text enclosed by (), [], or {} inclusive
    input_str = (
        re.sub(r'[\(\[\{][^\)\]\}]*[\)\]\}]', '', input_str) 
        if remove_brackets else input_str
    )

    if cutoff_str:
        cutoff_index = input_str.find(cutoff_str)
        if cutoff_index != -1:
            input_str = input_str[:cutoff_index].strip()

    if max_words > 0:
        words = input_str.split()
        input_str = ' '.join(words[:max_words])
    
    return input_str

if __name__ == "__main__":
    response = requests.get(url)
    calendar = Calendar(response.text)

    events = [
        event for event in calendar.events if 
        after < event.begin.datetime < before 
        and event.name not in exclude_strings
    ]
    
    # Sort events by due date
    events.sort(key=lambda event: event.begin.datetime)

    with open(path, 'w') as f:
        for event in events:
            task_name = format_string(event.name, 5, " - Due")
            due_date = event.begin.strftime('%Y-%m-%d')
            f.write(f"- [ ] {task_name} 📅 {due_date}\n")

    print(f"Tasks exported to {path}")
