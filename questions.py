import json
from random import choice as randchoice
from random import shuffle as randshuffle

from miscellaneous import hasher


def answerify(given_answer: str) -> str:
    return given_answer.strip().replace(" ", "").casefold()


def get_questions() -> list:
    with open("./questions.json", "r") as f:
        question_list = json.load(f)
    return question_list


class Question:
    def __init__(self, question_num_in_list: int):
        question = get_questions()[int(question_num_in_list) - 1]
        print(question)
        self.type = question["type"]
        self.question_text = ""
        self.image_url = ""
        if self.type == "i":
            self.image_url = question["text"]
        elif self.type == "t":
            self.text = question["text"]
        self.answer = answerify(question["ans"])
        self.smol_ans = hasher(self.answer)
        self.difficulty = question["difficulty"]
        self.number = question["no"]

    def check_answer(self, given_answer: str) -> bool:
        if answerify(given_answer) == self.answer:
            return True
        return False


def get_question_object(question_number: int) -> Question:
    return Question(question_number)


def get_answer_for_a_question(question_number: int | str = 1) -> str:
    q = Question(question_number)
    return q.answer


def get_personal_current_question(regno: str) -> Question:
    from firebase_functions import get_team_details

    current_question = get_team_details(regno, "current_question")
    sequence = get_team_details(regno, "sequence")

    player_sequence = str_sequence_to_int_list(sequence)
    
    return get_question_object(player_sequence[current_question - 1])


# -----------------------------------------------------------------


def str_sequence_to_int_list(sequence: str) -> list[int]:
    to_return = sequence.strip("[").strip("]").split(",")
    for i in range(len(to_return)):
        to_return[i] = int(to_return[i].strip().strip("'"))
    return to_return


def get_specific_difficulty_questions(question_dict: dict, difficuty: str) -> list[int]:
    to_return = [
        i
        for i in range(len(question_dict))
        if question_dict[i]["difficulty"].casefold() == difficuty.casefold()
    ]
    return to_return if to_return else []


def generate_sequence_for_a_team() -> list[int]:
    """Generates a sequence of questions for each team."""
    question_dict = get_questions()
    easy_questions = get_specific_difficulty_questions(question_dict, "easy")
    medium_questions = get_specific_difficulty_questions(question_dict, "medium")
    hard_questions = get_specific_difficulty_questions(question_dict, "hard")
    # print(easy_questions, medium_questions, hard_questions)
    sequence = []
    if easy_questions:
        randshuffle(easy_questions)
        sequence += easy_questions
    if medium_questions:
        randshuffle(medium_questions)
        sequence += medium_questions
    if hard_questions:
        randshuffle(hard_questions)
        sequence += hard_questions
    return sequence


# -----------------------------------------------------------------
