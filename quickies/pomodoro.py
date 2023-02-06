#! python
import os
import time
import math
import sys
import argparse
import winsound
import enum
import win32com.client
import rich
from rich.table import Table
from rich.live import Live


class states(enum.Enum):
    none = 0
    work = 1
    short_rest = 2
    long_rest = 3


debug = False

pomodoro_defaults = {states.work: 45 * 60, states.long_rest: 15 * 60, states.short_rest: 7.5 * 60}
sec = 0.99 if not debug else 0.0099
if debug:
    pomodoro_defaults = {states.work: 3, states.long_rest: 2, states.short_rest: 1}

_PD = pomodoro_defaults

state_strings = {
    states.none: "none",
    states.work: "work",
    states.long_rest: "long rest",
    states.short_rest: "short rest",
}


def get_next_state(current, prev=states.long_rest):
    if current == states.work:
        return states.short_rest if prev == states.long_rest else states.long_rest
    elif current == states.short_rest:
        return states.work
    elif current == states.long_rest:
        return states.work
    elif current == states.none:
        return states.work


class Beep:
    long_freq = 440
    long_dur = 1500
    long_wait = 450

    long_tts = f"{int(_PD[states.long_rest]/60)} minute break"

    short_freq = 500
    short_dur = 750
    short_wait = 250
    short_tts = f"{int(_PD[states.short_rest]/60)} minute break"

    work_freq = 400
    work_dur = 1000
    work_wait = 300
    work_tts = f"{int(_PD[states.work]/60)} work interval"

    @classmethod
    def play(cls, state=states.short_rest):
        if state == states.short_rest:
            freq = cls.short_freq
            dur = cls.short_dur
            wait = cls.short_wait
            tts = cls.short_tts
        elif state == states.long_rest:
            freq = cls.long_freq
            dur = cls.long_dur
            wait = cls.long_wait
            tts = cls.long_tts
        elif state == states.work:
            freq = cls.work_freq
            dur = cls.work_dur
            wait = cls.work_wait
            tts = cls.work_tts
        cls.make_sound(freq, dur, tts)

    @classmethod
    def make_sound(cls, freq, dur, tts):
        # winsound.Beep(frequency=freq, duration=dur)
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        speaker.Speak(tts)


class Runner:
    def __init__(self, work_intervals=4, state=None):
        self.state = states.work
        self.prev_state = states.long_rest
        self.work_intervals = work_intervals
        self.second_iter = 0
        self.interval_iter = 0
        self.current_time_interval = _PD[self.state]
        self.current_str = ""

    def transition(self):
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        speaker.Speak("ending")

        Beep.play(self.state)
        new_state = get_next_state(self.state, self.prev_state)
        self.prev_state = self.state
        self.state = new_state
        self.current_time_interval = _PD[self.state]
        self.second_iter = 0
        speaker.Speak("starting")
        Beep.play(self.state)

    def get_time_string(self):
        minutes = math.floor(self.second_iter / 60)
        seconds = self.second_iter % 60

        state_str = state_strings[self.state]

        end_min = math.floor(self.current_time_interval / 60)
        end_sec = "00"

        return f"[{state_str}] - {minutes}:{seconds} / {end_min}:{end_sec}"

    def do_main(self):

        Beep.play(self.state)
        while self.interval_iter < self.work_intervals:
            while self.second_iter < self.current_time_interval:
                # self.current_str = self.get_time_string()
                time.sleep(0.01)
                self.second_iter += 1
            if self.state == states.work:
                self.interval_iter += 1
            self.transition()

    def main_loop(self):
        while self.interval_iter < self.work_intervals:
            self.periodic()
            time.sleep(0.01)

    def periodic(self):
        if self.interval_iter >= self.work_intervals:
            quit(0)
        if self.second_iter < self.current_time_interval:
            self.current_str = self.get_time_string()
            self.second_iter += 1
        else:
            if self.state == states.work:
                self.interval_iter += 1
            self.transition()


def main(args):
    print(__file__, args.__dict__)
    # return
    runner = Runner(args.intervals)
    while runner.interval_iter < runner.work_intervals:

        runner.periodic()
        os.system("clear")
        print(f"{runner.get_time_string()}\n")
        time.sleep(sec)

    time.sleep(sec)
    # def make_table():
    #     table = Table()
    #     table.add_column("pomodoro")
    #     table.add_row(runner.get_time_string())
    #     return table

    # with Live(make_table(), refresh_per_second=1) as live:

    # runner.do_main()


def parse_args(args_):
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--intervals", dest="intervals", default=4, help="how many work intervals are there")
    return parser.parse_args(args_)


if __name__ == "__main__":
    main(parse_args(sys.argv[1:]))
