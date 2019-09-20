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

The women sat in a row\. They all wore different colors and (?P<person1>\w+ \w+)
wore a jaunty (?P<color1>\w+) hat\. (?P<person2>\w+ \w+) was at the far left,
next to the guest wearing a (?P<color2>\w+) jacket\. The lady in (?P<color3>\w+) sat left of
someone in (?P<color4>\w+)\. I remember that \w+ outfit because the woman
spilled her (?P<drink1>\w+) all over it\. The traveler from (?P<town1>\w+) was dressed
entirely in (?P<color5>\w+)\. When one of the dinner guests bragged about her
(?P<heirloom1>\w+( \w+)?), the woman next to her said they were finer in (?P<town2>\w+),
where she lived\.

So (?P<person3>\w+ \w+) showed off a prized (?P<heirloom2>\w+( \w+)?), at which the lady from
(?P<town3>\w+) scoffed, saying it was no match for her (?P<heirloom3>\w+( \w+)?)\.
Someone else carried a valuable (?P<heirloom4>\w+( \w+)?) and when she saw it,
the visitor from (?P<town4>\w+) next to her almost spilled her neighbor's
(?P<drink2>\w+)\. (?P<person4>\w+ \w+) raised her (?P<drink3>\w+) in toast\. The lady from (?P<town5>\w+),
full of (?P<drink4>\w+), jumped up onto the table, falling onto the guest in the
center seat, spilling the poor woman's (?P<drink5>\w+)\. Then (?P<person5>\w+ \w+)
captivated them all with a story about her wild youth in (?P<town6>\w+)\.

In the morning, there were four heirlooms under the table: (the )?\w+( \w+)?,
(the )?\w+( \w+)?, (the )?\w+( \w+)?, and (the )?\w+( \w+)?\.

But who owned each\?
"""

puzzle = " ".join(puzzle.split("\n"))
pattern = " ".join(pattern.split("\n"))
match = re.fullmatch(pattern, puzzle)

determined = [
    match.group("color1", "person1"),
    ("first", match.group("person2")),
    match.group("heirloom2", "person3"),
    match.group("drink3", "person4"),
    match.group("town6", "person5"),
]

for variable, name in determined:
    jindosh_puzzle.addConstraint(
        lambda variable, name=name: variable == name, [variable]
    )

equal_variables = [
    ("second", match.group("color2")),
    match.group("color3", "drink1"),
    match.group("town1", "color5"),
    match.group("town3", "heirloom3"),
    match.group("town5", "drink4"),
    ("third", match.group("drink5")),
]

for equal in equal_variables:
    jindosh_puzzle.addConstraint(AllEqualConstraint(), equal)


def complex_constraintown1(color3, color4, *seats):
    """The lady in <color3> sat left of someone in <color4>."""
    if seats[-1] == color3:
        return False
    return seats[seats.index(color3) + 1] == color4


jindosh_puzzle.addConstraint(
    complex_constraintown1, [match.group("color3"), match.group("color4"), *seats]
)


def get_neighbouring_seat(i, seats):
    if i == 0:
        return [(1, seats[1])]
    elif i == len(seats) - 1:
        return [(len(seats) - 1, seats[len(seats) - 1])]
    else:
        return [(i - 1, seats[i - 1]), (i + 1, seats[i + 1])]


def complex_constraintown2(heirloom1, town2, *seats):
    """When one of the dinner guests bragged about her
    <heirloom1>, the woman next to her said they were finer in <town2>,
    where she lived."""
    return any(seat == town2 for _, seat in get_neighbouring_seat(seats.index(heirloom1), seats))


jindosh_puzzle.addConstraint(
    complex_constraintown2, [match.group("heirloom1"), match.group("town2"), *seats]
)


def complex_constraintown3(heirloom4, town4, drink2, *seats):
    """Someone else carried a valuable <heirloom4> and when she saw it,
    the visitor from <town4> next to her almost spilled her neighbor's
    <drink2>."""
    return any(
        seat == town4 and any(seat == drink2 for _, seat in get_neighbouring_seat(j, seats))
        for j, seat in get_neighbouring_seat(seats.index(heirloom4), seats)
    )


jindosh_puzzle.addConstraint(
    complex_constraintown3,
    [match.group("heirloom4"), match.group("town4"), match.group("drink2"), *seats],
)
solution = jindosh_puzzle.getSolution()
ordered_names = [solution[seat] for seat in seats]
item_by_name = {solution[item]: item for item in items}
for name in ordered_names:
    print(f"{name}: {item_by_name[name]}")
