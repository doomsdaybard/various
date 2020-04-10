#!/usr/bin/python
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from math import ceil
from string import Template
import csv
import argparse

tax = Decimal('.05')
prec = Decimal('.01')

parser = argparse.ArgumentParser()
parser.add_argument('quarter', type=int)
parser.add_argument('file', type=open)
parser.add_argument('templatefile', type=open)

args = parser.parse_args()

data = []

with args.file as f:
    reader = csv.reader(f, delimiter=';')
    next(reader, None)
    for row in reader:
        date = datetime.strptime(row[5].strip(), "%d.%m.%Y").date()
        money = Decimal(row[11].strip().replace(" ", ""))
        if money > 0:
            data.append((date, money))

quarters = [[] for _ in range(4)]

for tuple in data:
    qr = ceil(tuple[0].month / 3)
    quarters[qr - 1].append(tuple)

total_sum = sum([item[1] for sublist in quarters[:args.quarter] for item in sublist])
total_sum_tax = total_sum * tax
total_sum_tax = total_sum_tax.quantize(prec, rounding=ROUND_HALF_UP)

if args.quarter - 1 > 0:
    prev_total_sum_tax = sum([item[1] for sublist in quarters[:args.quarter - 1] for item in sublist]) * tax
    prev_total_sum_tax = prev_total_sum_tax.quantize(prec, rounding=ROUND_HALF_UP)
else:
    prev_total_sum_tax = Decimal(0)

expected_quarter_sum_tax = sum(list(zip(*quarters[args.quarter - 1]))[1]) * tax
expected_quarter_sum_tax = expected_quarter_sum_tax.quantize(prec, rounding=ROUND_HALF_UP)
actual_quarter_sum_tax = total_sum_tax - prev_total_sum_tax

if expected_quarter_sum_tax != actual_quarter_sum_tax:
    print("WARNING: expected and actual quarter sum taxes are not equal")
    print("actual =", actual_quarter_sum_tax)
    print("expected =", expected_quarter_sum_tax)
    exit(1)

# print("total sum =", total_sum)
# print("total sum tax =", total_sum_tax)
# print("previous total sum tax =", prev_total_sum_tax)
# print("quarter tax =", actual_quarter_sum_tax)

header_period_map = {
    3: ("1KV", 2),
    6: ("HY", 3),
    9: ("3KV", 4),
    12: ("Y", 5)
}

period_month = args.quarter * 3
headertuple = header_period_map[period_month]

mapping = {
    "PERIOD_MONTH": period_month,
    "PERIOD_TYPE": headertuple[1],
    "CURRENT_YEAR": datetime.now().year,
    "HTYPE": headertuple[0],
    "TOTAL_SUM": total_sum,
    "TOTAL_SUM_TAX": total_sum_tax,
    "QUARTER_TAX": actual_quarter_sum_tax,
    "DATE": datetime.now().strftime("%d%m%Y")
}

if not args.quarter - 1 > 0:
    mapping["ROW_PREV_TOTAL_SUM_TAX"] = ""
else:
    mapping["ROW_PREV_TOTAL_SUM_TAX"] = "\n<R013G3>%s</R013G3>" % prev_total_sum_tax

with args.templatefile as templ:
    result = Template(templ.read())
    print(result.safe_substitute(mapping))
