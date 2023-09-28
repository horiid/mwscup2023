#!/usr/bin/env python3

import csv

file = "search_words.csv"
words_list = []

with open(file, encoding="utf-8", newline="") as f:
    cr = csv.reader(f)
    for row in cr:
        words_list.append(row[0])

print(words_list)


# 表示確認（あとで消す）
print(words_list[0])
print(words_list[1])
