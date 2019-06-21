import sys
import os
import csv
from bs4 import BeautifulSoup

# If true, only include posts with a score greater than the defined threshold
# (limits size of output graph)
LIMIT_OUTPUT = True
SCORE_THRESHOLD = 10

INPUT_DIR = "xml_inputs"
OUTPUT_DIR = "csv_files"

# Helper functions
def sanitize_string(in_string):
    if not in_string or len(in_string) <= 1:
        return None

    # Remove all HTML tags from string
    sanitized = BeautifulSoup(in_string, "lxml").text
    # remove internal newlines
    return sanitized.replace('\n', ' ') # .replace('\r', '')

# Convert integer to string if possible
def get_integer(in_string):
    try:
        return int(float(in_string))
    except:
        return 0

# Make unique IDs for users, as otherwise they'll clash with posts
def generate_user_id(id_str):
    try:
        return 'user_' + id_str
    except:
        return None

# Process Posts file to generate question and answer nodes and ANSWERED edges
def process_posts():
    with open(os.path.join(INPUT_DIR, "Posts.xml"), 'r') as posts_in,             \
         open(os.path.join(OUTPUT_DIR, "Question.csv"), 'w') as questions_out,    \
         open(os.path.join(OUTPUT_DIR, "Answer.csv"), 'w') as answers_out,        \
         open(os.path.join(OUTPUT_DIR, "AUTHOR_OF.csv"), 'w') as author_edge_out,      \
         open(os.path.join(OUTPUT_DIR, "HAS_TAG.csv"), 'w') as tag_edge_out:


        # Open CSV writers
        questions_writer = csv.writer(questions_out, quoting=csv.QUOTE_MINIMAL)
        answers_writer = csv.writer(answers_out, quoting=csv.QUOTE_MINIMAL)
        author_edge_writer = csv.writer(author_edge_out, quoting=csv.QUOTE_MINIMAL)
        tag_edge_writer = csv.writer(tag_edge_out, quoting=csv.QUOTE_MINIMAL)

        # Write headers
        questions_writer.writerow(['_id', 'score', 'title', 'text'])
        answers_writer.writerow(['_id', 'score', 'text'])
        author_edge_writer.writerow(['user_id', 'post_id'])
        tag_edge_writer.writerow(['question', 'tag'])

        answered_edge_hash = {}
        tag_set = set()
        question_set = set()
        answer_set = set()

        soup = BeautifulSoup(posts_in, "lxml")
        for row in soup.find_all('row'):
            row_id = get_integer(row.get('id'))
            user_id = generate_user_id(row.get('owneruserid'))
            # Skip bot-written posts
            if user_id == 'user_-1':
                continue

            post_type = get_integer(row.get('posttypeid'))
            # Skip posts that are neither questions (1) nor answers (2)
            if post_type > 2:
                continue

            score = get_integer(row.get('score'))
            # Skip post if we're trimming output and the post's score is low
            if LIMIT_OUTPUT and score < SCORE_THRESHOLD:
                continue

            # Collect data to be stored on entity
            converted = {}
            converted['id'] = row_id
            converted['score'] = score

            if post_type == 1: # question
                converted['title'] = row.get('title')
                converted['text'] = sanitize_string(row.get("body"))
                questions_writer.writerow(converted.values())
                question_set.add(row_id) # Track which questions we've kept

                # Add an edge from the question to each of its tags
                tag_str = row.get('tags')
                if tag_str:
                    # Omit first and last characters, which are tag separators
                    tag_list = tag_str[1:-1].split('><')
                    for tag in tag_list:
                        tag_set.add(tag)
                        tag_edge_writer.writerow([row_id, tag])

                try:
                    accepted_id = int(float((row.get("acceptedanswerid"))))
                    answered_edge_hash[accepted_id] = [row_id, True]
                except:
                    pass # No accepted answer
            elif post_type == 2: # answer
                parent_id = get_integer(row.get('parentid'))
                if parent_id not in question_set: # Skip answers to skipped questions
                    continue

                converted['text'] = sanitize_string(row.get("body"))
                answer_set.add(row_id)

                if row_id not in answered_edge_hash:
                    answered_edge_hash[row_id] = [parent_id, False]
                answers_writer.writerow(converted.values())

            # Write relation between post and author
            if user_id:
                author_edge_writer.writerow([user_id, row_id])

    # Output file for ANSWERED relations
    with open(os.path.join(OUTPUT_DIR, "ANSWER_TO.csv"), 'w') as answered_edge_out:
        answered_writer = csv.writer(answered_edge_out, quoting=csv.QUOTE_MINIMAL)

        # Populate ANSWERED relation with source, dest, and a boolean for whether the answer was accepted
        answered_writer.writerow(['answer_id', 'question_id', 'accepted'])
        for answer, question in answered_edge_hash.items():
            if answer not in answer_set:
                continue
            answered_writer.writerow([answer, question[0], question[1]])

    with open(os.path.join(OUTPUT_DIR, "Tag.csv"), 'w') as tag_out:
        tag_writer = csv.writer(tag_out, quoting=csv.QUOTE_MINIMAL)
        # Tag file header
        tag_writer.writerow(['name'])
        for tag in tag_set:
            tag_writer.writerow([tag])

# Process Users file
def process_users():
    with open(os.path.join(INPUT_DIR, "Users.xml"), 'r') as users_in,     \
         open(os.path.join(OUTPUT_DIR, "User.csv"), 'w') as users_out:

        users_writer = csv.writer(users_out, quoting=csv.QUOTE_MINIMAL)
        users_writer.writerow(['_user_id', 'name', 'reputation'])

        soup = BeautifulSoup(users_in, "lxml")
        for row in soup.find_all('row'):
            converted = {}
            user_id = generate_user_id(row.get('id'))
            if not user_id:
                continue

            converted['_user_id'] = user_id
            converted['name'] = row.get('displayname')
            converted['reputation'] = get_integer(row.get('reputation'))

            users_writer.writerow(converted.values())


if sys.version_info[0] < 3:
    raise Exception("Python 3 required for parse script.")

process_posts()
process_users()
