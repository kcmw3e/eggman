# MIT License
# 
# Copyright (c) 2022 kcmw3e
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import math

import discord

INFO_LINE = 0
PADDING_LINE = 1
GUESS_LINES_START = 2

WORDLE_RESULT_MIN_LINES = 3
WORDLE_RESULT_PREFIX = "Wordle"

INFO_LINE_NUM_CMOMPONENTS = len(["Wordle", "Day", "Score"])
INFO_WORDLE_RESULT_PREFIX_INDEX = 0
INFO_DAY_INDEX = 1
INFO_SCORE_INDEX = 2

SCORE_MIN_LEN = 3
SCORE_HARDMODE_LEN = 4
SCORE_FAILED_CHAR = "X"
SCORE_OUTOF_CHAR = "/"
SCORE_NUM_OUTOF = "6"
SCORE_HARDMODE_CHAR = "*"
SCORE_FAILED_INT = 7
SCORE_NUM_GUESSES_INDEX = 0
SCORE_OUTOF_CHAR_INDEX = 1
SCORE_NUM_OUTOF_INDEX = 2
SCORE_HARDMODE_CHAR_INDEX = 3

GREEN_SQUARE =  "\U0001f7e9"
BLACK_SQUARE =  "\u2b1b"
YELLOW_SQUARE = "\U0001f7e8"

BOX_ONE = "1\ufe0f\u20e3"
BOX_TWO = "2\ufe0f\u20e3"
BOX_THREE = "3\ufe0f\u20e3"
BOX_FOUR = "4\ufe0f\u20e3"
BOX_FIVE = "5\ufe0f\u20e3"
BOX_SIX = "6\ufe0f\u20e3"
BOX_X = "\U0001f1fd"
BOX_X_RED = "\u274c"
BOX_X_BLACK = "\u2716\ufe0f"

DISTRIBUTION_LEN = 20

class Wordlestats(object):
    @staticmethod
    def is_wordle_guess(s:str):
        s = s.replace(YELLOW_SQUARE, "")
        s = s.replace(GREEN_SQUARE, "")
        s = s.replace(BLACK_SQUARE, "")
        return s == ""

    @staticmethod
    def is_wordle_result(s:str):
        return Wordlestats.get_wordle_result(s) != None

    @staticmethod
    def get_wordle_result(s:str):

        lines = s.splitlines()
        if (len(lines) < WORDLE_RESULT_MIN_LINES): return None

        info_line = lines[INFO_LINE]
        pad_line = lines[PADDING_LINE]
        guess_lines = lines[GUESS_LINES_START:]

        info = info_line.split()
        if (len(info) != INFO_LINE_NUM_CMOMPONENTS): return None

        if (info[INFO_WORDLE_RESULT_PREFIX_INDEX] != WORDLE_RESULT_PREFIX): return None
        
        day_str = info[INFO_DAY_INDEX]
        if (not day_str.isnumeric()): return None
        day = int(day_str)
        
        score_str = info[INFO_SCORE_INDEX]
        if (len(score_str) != SCORE_MIN_LEN and len(score_str) != SCORE_HARDMODE_LEN):
            return None

        if (score_str[SCORE_OUTOF_CHAR_INDEX] != SCORE_OUTOF_CHAR): return None

        if (score_str[SCORE_NUM_OUTOF_INDEX] != SCORE_NUM_OUTOF): return None

        num_guesses = score_str[SCORE_NUM_GUESSES_INDEX]
        if (not num_guesses.isnumeric() and num_guesses != SCORE_FAILED_CHAR): return None
        score = int(num_guesses) if (num_guesses != SCORE_FAILED_CHAR) else SCORE_FAILED_INT

        if (len(score_str) == SCORE_HARDMODE_LEN):
            score_hardmode_str = score_str[SCORE_HARDMODE_CHAR_INDEX]
            if (score_hardmode_str != SCORE_HARDMODE_CHAR): return None
            hardmode = True
        else:
            hardmode = False

        guesses = []
        for (i, guess_line) in enumerate(guess_lines):
            if (not Wordlestats.is_wordle_guess(guess_line)):
                if (i == 0): return None
                break
            guesses.append(guess_line)

        # could grab stats on yellows, grays, etc from here, but leaving it at this for now
        result = {
            "score": score,
            "hardmode": hardmode,
            "guesses": guesses
        }
        return (day, result)
        

    def __init__(self, author):
        self.author = author
        self.wordles = dict()
        self.longest_streak = 0
        self.scorenums = [0, 0, 0, 0, 0, 0, 0]
        self.scorecents = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    def add_wordle(self, wordle_day, wordle_result):
        self.wordles[wordle_day] = wordle_result
        self.update_stats()

    def num_wordles(self):
        return len(self.wordles.keys())

    def update_stats(self):
        self.find_longest_streak()
        self.find_scorenums()
        self.find_scorecents()

    def find_longest_streak(self):
        days = list(self.wordles.keys())

        longest_streak = 0
        curr_streak = 0
        prev_day = 0
        for day in sorted(days):
            score = self.wordles[day]["score"]
            if (day - 1 == prev_day and score != SCORE_FAILED_INT): curr_streak += 1
            elif score != SCORE_FAILED_INT: curr_streak = 1
            else: curr_streak = 0
            prev_day = day
            longest_streak = max(longest_streak, curr_streak)
        self.longest_streak = longest_streak
        
    def find_scorenums(self):
        scorenums = [0, 0, 0, 0, 0, 0, 0] # [1s, 2s, 3s, 4s, 5s, 6s, Xs]
        for day in self.wordles.keys():
            wordle = self.wordles[day]
            score = wordle["score"]
            scorenums[score - 1] += 1
        self.scorenums = scorenums

    def find_scorecents(self):
        for i in range(len(self.scorenums)):
            self.scorecents[i] = (self.scorenums[i]/self.num_wordles())*100

    def stats_str(self, show_percent = False, show_dist = False):
        stats = self.scorenums
        
        if (show_percent):
            for i in range(len(self.scorecents)):
                stats[i] = f"{self.scorecents[i]:.2f}"
        
        if (show_dist):
            for i in range(len(self.scorecents)):
                perc = self.scorecents[i]
                greens = math.ceil(DISTRIBUTION_LEN*perc/100)
                blacks = DISTRIBUTION_LEN - greens
                squares = f"{GREEN_SQUARE*greens}{BLACK_SQUARE*blacks}"
                stats[i] = squares
        
        s = f"{self.author.name}'s wordle stats\n\
              Longest streak: {self.longest_streak}\n\
              {BOX_ONE} {stats[0]}\n\
              {BOX_TWO} {stats[1]}\n\
              {BOX_THREE} {stats[2]}\n\
              {BOX_FOUR} {stats[3]}\n\
              {BOX_FIVE} {stats[4]}\n\
              {BOX_SIX} {stats[5]}\n\
              {BOX_X} {stats[6]}\n"

        return s
