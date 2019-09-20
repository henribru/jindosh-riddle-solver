import itertools
import re
from constraint import Problem, AllDifferentConstraint, AllEqualConstraint

names = [
    "Lady Winslow",
    "Doctor Marcolla",
    "Countess Contee",
    "Madam Natsiou",
    "Baroness Finch",
]

seats = ["first", "second", "third", "fourth", "fifth"]
colors = ["blue", "purple", "red", "green", "white"]
items = ["Snuff Tin", "Ring", "War Medal", "Bird Pendant", "Diamond"]
locations = ["Baleton", "Dunwall", "Dabokva", "Karnaca", "Fraeport"]
drinks = ["wine", "beer", "rum", "whiskey", "absinthe"]

jindosh_puzzle = Problem()
jindosh_puzzle.addVariables(
    list(itertools.chain(seats, colors, items, locations, drinks)), names
)

for variable_type in [seats, colors, items, locations, drinks]:
    jindosh_puzzle.addConstraint(AllDifferentConstraint(), variable_type)


puzzle = """
At the dinner party were Lady Winslow, Doctor Marcolla, Countess
Contee, Madam Natsiou, and Baroness Finch.

The women sat in a row. They all wore different colors and Doctor
Marcolla wore a jaunty blue hat. Countess Contee was at the far left,
next to the guest wearing a purple jacket. The lady in red sat left of
someone in green. I remember that red outfit because the woman
spilled her wine all over it. The traveler from Baleton was dressed
entirely in white. When one of the dinner guests bragged about her
Snuff Tin, the woman next to her said they were finer in Baleton,
where she lived.

So Madam Natsiou showed off a prized Ring, at which the lady from
Dunwall scoffed, saying it was no match for her War Medal.
Someone else carried a valuable Bird Pendant and when she saw it,
the visitor from Dabokva next to her almost spilled her neighbor's
beer. Baroness Finch raised her rum in toast. The lady from Karnaca,
full of whiskey, jumped up onto the table, falling onto the guest in the
center seat, spilling the poor woman's absinthe. Then Lady Winslow
captivated them all with a story about her wild youth in Fraeport.

In the morning, there were four heirlooms under the table: the Snuff Tin,
Diamond, the War Medal, and the Bird Pendant.

But who owned each?
"""

pattern = r"""
At the dinner party were Lady Winslow, Doctor Marcolla, Countess
Contee, Madam Natsiou, and Baroness Finch\.

The women sat in a row\. They all wore different colors and (?P<p1>\w+ \w+)
wore a jaunty (?P<c1>\w+) hat\. (?P<p2>\w+ \w+) was at the far left,
next to the guest wearing a (?P<c2>\w+) jacket\. The lady in (?P<c3>\w+) sat left of
someone in (?P<c4>\w+)\. I remember that \w+ outfit because the woman
spilled her (?P<d1>\w+) all over it\. The traveler from (?P<t1>\w+) was dressed
entirely in (?P<c5>\w+)\. When one of the dinner guests bragged about her
(?P<h1>\w+( \w+)?), the woman next to her said they were finer in (?P<t2>\w+),
where she lived\.

So (?P<p3>\w+ \w+) showed off a prized (?P<h2>\w+( \w+)?), at which the lady from
(?P<t3>\w+) scoffed, saying it was no match for her (?P<h3>\w+( \w+)?)\.
Someone else carried a valuable (?P<h4>\w+( \w+)?) and when she saw it,
the visitor from (?P<t4>\w+) next to her almost spilled her neighbor's
(?P<d2>\w+)\. (?P<p4>\w+ \w+) raised her (?P<d3>\w+) in toast\. The lady from (?P<t5>\w+),
full of (?P<d4>\w+), jumped up onto the table, falling onto the guest in the
center seat, spilling the poor woman's (?P<d5>\w+)\. Then (?P<p5>\w+ \w+)
captivated them all with a story about her wild youth in (?P<t6>\w+)\.

In the morning, there were four heirlooms under the table: (the )?\w+( \w+)?,
(the )?\w+( \w+)?, (the )?\w+( \w+)?, and (the )?\w+( \w+)?\.

But who owned each\?
"""

puzzle = " ".join(puzzle.split("\n"))
pattern = " ".join(pattern.split("\n"))
match = re.fullmatch(pattern, puzzle)

determined = [
    match.group("c1", "p1"),
    ("first", match.group("p2")),
    match.group("h2", "p3"),
    match.group("d3", "p4"),
    match.group("t6", "p5"),
]

for variable, name in determined:
    jindosh_puzzle.addConstraint(
        lambda variable, name=name: variable == name, [variable]
    )

equal_variables = [
    ("second", match.group("c2")),
    match.group("c3", "d1"),
    match.group("t1", "c5"),
    match.group("t3", "h3"),
    match.group("t5", "d4"),
    ("third", match.group("d5")),
]

for equal in equal_variables:
    jindosh_puzzle.addConstraint(AllEqualConstraint(), equal)


def complex_constraint1(c3, c4, *seats):
    """The lady in <c3> sat left of someone in <c4>."""
    if seats[-1] == c3:
        return False
    return seats[seats.index(c3) + 1] == c4


jindosh_puzzle.addConstraint(
    complex_constraint1, [match.group("c3"), match.group("c4"), *seats]
)


def get_neighbouring_seat(i, seats):
    if i == 0:
        return [(1, seats[1])]
    elif i == len(seats) - 1:
        return [(len(seats) - 1, seats[len(seats) - 1])]
    else:
        return [(i - 1, seats[i - 1]), (i + 1, seats[i + 1])]


def complex_constraint2(h1, t2, *seats):
    """When one of the dinner guests bragged about her
    <h1>, the woman next to her said they were finer in <t2>,
    where she lived."""
    return any(seat == t2 for _, seat in get_neighbouring_seat(seats.index(h1), seats))


jindosh_puzzle.addConstraint(
    complex_constraint2, [match.group("h1"), match.group("t2"), *seats]
)


def complex_constraint3(h4, t4, d2, *seats):
    """Someone else carried a valuable <h4> and when she saw it,
    the visitor from <t4> next to her almost spilled her neighbor's
    <d2>."""
    return any(
        seat == t4 and any(seat == d2 for _, seat in get_neighbouring_seat(j, seats))
        for j, seat in get_neighbouring_seat(seats.index(h4), seats)
    )


jindosh_puzzle.addConstraint(
    complex_constraint3,
    [match.group("h4"), match.group("t4"), match.group("d2"), *seats],
)
solution = jindosh_puzzle.getSolution()
ordered_names = [solution[seat] for seat in seats]
item_by_name = {solution[item]: item for item in items}
for name in ordered_names:
    print(f"{name}: {item_by_name[name]}")
