#! /usr/bin/env python
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

    def get(self, thing):
        if str(thing).isnumeric():
            return self._get_by_int(int(thing))
        else:
            return self._get_by_name(thing)

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

    def quiz_main(self, num_questions=1):
        num_correct = 0
        for _ in range(num_questions):
            if self._quiz_question():
                num_correct += 1
        print(f"You got {num_correct} out of {num_questions} correct")

    def _quiz_get_name(self, card):
        "get name of card"
        return card.name

    def _quiz_get_upright(self, card):
        "get upright reading"
        return card.upright

    def _quiz_get_number(self, card):
        "get number of card"
        return card.number

    def _quiz_get_input(self):
        "get input from user"
        value = None
        while value is None:
            _value = input("> ")
            if _value.isnumeric() and int(_value) in range(0, 5):
                value = int(_value)
        return value

    def _quiz_question(self):
        """print name, provide random choices, ask for answer, return True/False"""
        this_qa_reverse = random.random() < 0.7
        this_qa_pair = random.choice(self.qa_pairs)

        question_func = this_qa_pair[0] if not this_qa_reverse else this_qa_pair[1]
        answer_func = this_qa_pair[1] if not this_qa_reverse else this_qa_pair[0]
        # question_func = self._quiz_get_name if this_qa_reverse else self._quiz_get_upright
        # answer_func = self._quiz_get_upright if this_qa_reverse else self._quiz_get_name

        card = self._draw()

        print(question_func(card))
        choices = [self._draw() for _ in range(3)]
        choices.append(card)
        random.shuffle(choices)
        enumerated_choices = list(choices)
        for i, choice in enumerate(choices):
            print(f"{i + 1}: {answer_func(choice)}")
        print("please enter the # of the correct answer?")
        answer = self._quiz_get_input()
        answer_index = int(answer) - 1
        correct_value = answer_func(card)
        chosen_value = answer_func(enumerated_choices[answer_index])
        is_correct = chosen_value == correct_value
        if is_correct:
            print("Correct!")
        else:
            print(f"Incorrect. The answer was:\n\t{answer_func(card)}")
        return is_correct


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("-i", "--info", type=str, nargs="*")
    args.add_argument("-r", "--reading", action="store_true", default=False)
    args.add_argument("-d", "--draw", type=int, nargs="*", default=None)
    args.add_argument("-q", "--quiz", type=int, nargs="?", default=1)
    args.add_argument("args", nargs="*")
    args = args.parse_args()
    print("\n")
    if args.quiz:
        print("q")
        TarotRunner().quiz_main(args.quiz)
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
