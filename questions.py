from json import load as jsonload
from random import choice as randchoice
from random import shuffle as randshuffle


def get_answer_for_a_question(question_no: int) -> str:
    return get_questions()[question_no - 1]["ans"]


def get_questions() -> list:
    with open("./questions.json", "r") as f:
        question_dict = jsonload(f)
    return question_dict


def get_specific_difficulty_questions(question_dict: dict, difficuty: str) -> list[str]:
    to_return = [
        str(i)
        for i in range(len(question_dict))
        if question_dict[i]["difficulty"].casefold() == difficuty.casefold()
    ]
    return to_return if to_return else []


def get_current_question():
    ...


def str_sequence_to_list_int(sequence: str) -> list[int]:
    to_return = sequence.strip("[").strip("]").split(",")
    for i in range(len(to_return)):
        to_return[i] = int(to_return[i].strip().strip("'"))
    return to_return


def generate_sequence_for_a_team() -> list[str]:
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


def get_question_for_a_question_number(question_number: int | str = 1):
    return get_questions[int(question_number) - 1]
