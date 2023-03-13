#! /usr/bin/env python
import sys
import math
import time
import random
from rich.console import Console
from rich.layout import Layout
from rich.text import Text
from rich.live import Live
import pprint
import json
import pathlib
import argparse
import logging
from Fuzzy import fuzzy_string_comparison, normalize_string

arcana_path = pathlib.Path(__file__).parent / "arcana.json"
_CARDS_DATA = None
CARDS = {}


class MajorArcana:
    join_char = "\n"

    def __init__(
        self,
        name,
        number,
        upright,
        reversed,
        stand_name=None,
        stand_user=None,
        stand_ability=None,
        is_reverse=False,
        *args,
        **kwargs,
    ) -> None:
        self.name = name
        self.number = number
        self.upright = upright
        self.reversed = reversed
        self.stand_name = kwargs.get("stand name", stand_name)
        self.stand_user = kwargs.get("stand user", stand_user)
        self.stand_ability = kwargs.get("stand ability", stand_ability)
        self.is_reverse = is_reverse

    def __str__(self):
        return self.join_char.join(
            [
                self.name,
                self.upright,
                self.reversed,
            ]
        )

    def get_dict(self):
        return {
            "name": self.name,
            "number": self.number,
            "upright": self.upright,
            "reversed": self.reversed,
            "stand_name": self.stand_name,
            "stand_user": self.stand_user,
            "stand_ability": self.stand_ability,
        }


with open(arcana_path, "r") as arcana_file:
    _CARDS_DATA = json.load(arcana_file)["major arcana"]

    for card in _CARDS_DATA:
        new_card = MajorArcana(**card)
        CARDS[card["name"].lower()] = new_card


class ArcanaDeck:
    reverse_odds = 0.3

    def __init__(self) -> None:
        self.cards_in_deck = [card for card in CARDS.values()]
        self.cards_played = []

    def draw(self):
        card = random.choice(self.cards_in_deck)
        card.is_reverse = random.random() < self.reverse_odds
        self.cards_in_deck.remove(card)
        self.cards_played.append(card)
        return card


class TarotRunner:
    def __init__(self) -> None:
        self.deck = ArcanaDeck()
        self.qa_pairs = [
            (self._quiz_get_name, self._quiz_get_number),
            (self._quiz_get_upright, self._quiz_get_name),
        ]
        self._blank_enty_pairs = [
            (self._quiz_get_name, self._quiz_get_number),
            (self._quiz_get_upright, self._quiz_get_name_normalized),
        ]
        self.fuzzy_comparison_threshold = 0.8

    def reading_main(self):
        console = Console()
        console.height = 10
        layout = Layout()
        layout.split_row(
            Layout(name="card1"), Layout(name="card2"), Layout(name="card3")
        )
        with Live(layout, console=console, screen=False) as livelayout:
            for i in range(3):
                cards = self.draw_three()
                for i, card in enumerate(cards):
                    layout[f"card{i + 1}"].update(self._draw_card_text(card))
            input()
        time.sleep(1)
        quit(0)

    def info_main(self, *args):
        for arg in args:
            card = self.get(arg)
            self._print_card_info(card)

    def get(self, thing):
        if str(thing).isnumeric():
            return self._get_by_int(int(thing))
        else:
            return self._get_by_name(thing)

    def quiz_main(self, num_questions=1):
        num_correct = 0
        for _ in range(num_questions):
            if self._quiz_question():
                num_correct += 1
        print(f"You got {num_correct} out of {num_questions} correct")

    def _quiz_question(self):
        """print name, provide random choices, ask for answer, return True/False"""
        question_func, answer_func, mode = self._quiz_get_qa_pair()
        is_correct = False
        if mode == "multiple choice":
            is_correct = self._quiz_multiple_choice_question(question_func, answer_func)
        elif mode == "blank entry":
            is_correct = self._quiz_blank_entry_question(question_func, answer_func)
        else:
            is_correct = self._quiz_say_upright_question()
        return is_correct

    def choose_mode(self):
        mc_weight = 2
        fill_in_weight = 1
        meaning_weight = 1
        sum_weights = mc_weight + fill_in_weight + meaning_weight
        mc_odds = mc_weight / sum_weights
        fill_in_odds = fill_in_weight / sum_weights
        meaning_odds = meaning_weight / sum_weights
        mode = None
        random_num = random.random()
        if random_num < mc_odds:
            mode = "multiple choice"
        elif random_num < mc_odds + fill_in_odds:
            mode = "blank entry"
        else:
            mode = "meaning"
        return mode

    def _quiz_get_qa_pair(self):
        question_func, answer_func = None, None
        reverse_odds = 0.5
        mode = self.choose_mode()
        if mode == "multiple choice":
            func_a, func_b = random.choice(self.qa_pairs)
            reverse_qa = random.random() < reverse_odds
            question_func = func_a if not reverse_qa else func_b
            answer_func = func_b if not reverse_qa else func_a
        elif mode == "blank entry":
            question_func, answer_func = random.choice(self._blank_enty_pairs)
        else:
            question_func = None
            answer_func = None
        return question_func, answer_func, mode

    def _quiz_multiple_choice_question(self, question_func, answer_func):
        card = self._draw()
        print(question_func(card))
        choices = [self._draw() for _ in range(3)]
        choices.append(card)
        random.shuffle(choices)
        enumerated_choices = list(choices)
        for i, choice in enumerate(choices):
            print(f"{i + 1}: {answer_func(choice)}")
        print("please enter the # of the correct answer?")
        answer = self._quiz_get_num_input()
        answer_index = int(answer) - 1
        correct_value = answer_func(card)
        correct_number_val = choices.index(card) + 1
        chosen_value = answer_func(enumerated_choices[answer_index])

        is_correct = chosen_value == correct_value
        if is_correct:
            print("Correct!")
        else:
            print(
                f"Incorrect. The answer was:\n\t{correct_number_val}) {answer_func(card)}"
            )
        return is_correct

    def _quiz_say_upright_question(self):
        """return correct if the user is able to say the upright meaning of the card"""
        card = self._draw()
        print(
            f"Please say atleast 2 things the following card represents, comma separated.\n\t{card.name}\n"
        )

        # print(card.upright)
        user_input = input()
        user_input_things = user_input.split(",")
        things_cards_means = card.upright.split(",")

        matches_to_score = 2
        current_matches = 0
        match_fuzz_threshold = 0.55
        for thing in user_input_things:
            rmv_answer = ""
            for card_meaning in things_cards_means:
                if fuzzy_string_comparison(thing, card_meaning) > match_fuzz_threshold:
                    current_matches += 1
                    things_cards_means.remove(card_meaning)
            if rmv_answer:
                things_cards_means.remove(rmv_answer)
        is_correct = current_matches >= matches_to_score
        if not is_correct:

            print(f"Incorrect. The answer was:\n\t{card.upright}")
            print(f"you had {current_matches} matches")
        else:
            print("Correct!")
            print("the other matches were: {}".format(", ".join(things_cards_means)))
        return is_correct

    def _quiz_get_name(self, card):
        "get name of card"
        return card.name

    def _quiz_get_name_normalized(self, card):
        "get name of card"
        return normalize_string(card.name.replace("The ", " "))

    def _quiz_get_upright(self, card):
        "get upright reading"
        return card.upright

    def _quiz_get_number(self, card):
        "get number of card"
        return card.number

    def _quiz_get_num_input(self):
        "get input from user"
        value = None
        while value is None:
            _value = input("> ")
            if _value.isnumeric() and int(_value) in range(0, 5):
                value = int(_value)
        return value

    def _quiz_get_str_input(self):
        "get input from user"
        value = None
        while value is None:
            _value = input("> ")
            if _value:
                value = _value
        return value

    def _quiz_blank_entry_question(self, question_func, answer_func):
        card = self._draw()
        print(question_func(card))
        answer = self._quiz_get_str_input()
        correct_value = answer_func(card)

        is_correct = self.fuzzy_comparison_threshold < self._quiz_fuzzy_compare(
            answer, correct_value
        )
        if is_correct:
            print("Correct!")
        else:
            print(f"Incorrect. The answer was:\n\t{answer_func(card)}")
        return is_correct

    def _quiz_fuzzy_compare(self, *args, **kwargs):
        return fuzzy_string_comparison(*args, **kwargs)

    def _get_by_int(self, i):
        if i > 22 or i < 0:
            print("Card number must be between 0 and 21")
        for card in CARDS.values():
            if card.number == i:
                return card

    def _get_by_name(self, name):
        for card in CARDS.values():
            if name.lower() in card.name.lower():
                return card
        else:
            print(f"Card {name} not found")
            return None

    def draw(self):
        card = self.deck.draw()
        name = card.name
        reading = card.upright if not card.is_reverse else card.reversed
        return f"{name} ({card.number})\n\t{reading}"

    def _draw(self):
        return self.deck.draw()

    def draw_three(self):
        return [self._draw() for _ in range(3)]

    def _print_card_info(self, card):
        pprint.pprint(card.get_dict(), sort_dicts=False)

    def _draw_card_text(self, card):
        text = Text()
        text.append(card.name, style="bold")
        rev_text = " (reversed)" if card.is_reverse else ""
        text.append(f" ({card.number}){rev_text}\n")
        if card.is_reverse:
            text.append(f"{card.reversed}", style="bold red")
        else:
            text.append(f"{card.upright}", style="bold green")
        return text


if __name__ == "__main__":
    # TarotRunner().quiz_main()
    # quit()
    args = argparse.ArgumentParser()
    args.add_argument("-i", "--info", type=str, nargs="*")
    args.add_argument("-r", "--reading", action="store_true", default=False)
    args.add_argument("-d", "--draw", type=int, nargs="*", default=None)
    args.add_argument("-q", "--quiz", type=int, nargs="*", default=1)
    args.add_argument("args", nargs="*")
    args = args.parse_args()

    # if q isn't there ignore default arg
    is_quiz = "-q" in sys.argv or "--quiz" in sys.argv

    print("\n")
    if is_quiz:
        # print("q")
        TarotRunner().quiz_main(*args.quiz)
    elif args.info:
        # print("info\n")
        TarotRunner().info_main(*args.info)
    elif args.reading:
        # print("reading\n")
        TarotRunner().reading_main()
    elif args.draw:
        # print("draw {} cards\n".format(args.draw))
        runner = TarotRunner()
        for _ in range(args.draw):
            print(runner.draw())
    else:
        print(TarotRunner().draw())
