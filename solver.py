import itertools
import re
from constraint import (  # type: ignore
    Problem,
    AllDifferentConstraint,
    AllEqualConstraint,
)
from typing import List, Tuple, Match, Sequence
import sys

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

variables = [*seats, *colors, *items, *locations, *drinks]

pattern = r"""At the dinner party were Lady Winslow, Doctor Marcolla, Countess
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

But who owned each\?"""
pattern = " ".join(pattern.split())


def main() -> None:
    riddle_text = get_riddle_text()
    match = re.fullmatch(pattern, riddle_text)
    if match is None:
        print("Something went wrong. Did you type the riddle correctly?")
        sys.exit(1)
    riddle = setup_riddle(match)
    solution = riddle.getSolution()
    item_by_name = {solution[item]: item for item in items}
    for i, seat in enumerate(seats, start=1):
        name = solution[seat]
        print(f"{i}: {name} - {item_by_name[name]}")


def get_riddle_text() -> str:
    with open("riddle.txt") as f:
        riddle = f.read()
    riddle = " ".join(riddle.strip().split())
    return riddle


def setup_riddle(match: Match[str]) -> Problem:
    riddle = Problem()
    riddle.addVariables(variables, names)

    for variable_group in [seats, colors, items, locations, drinks]:
        riddle.addConstraint(AllDifferentConstraint(), variable_group)

    determined_pairs: List[Tuple[str, str]] = [
        match.group("color1", "person1"),  # type: ignore
        ("first", match.group("person2")),
        match.group("heirloom2", "person3"),  # type: ignore
        match.group("drink3", "person4"),  # type: ignore
        match.group("town6", "person5"),  # type: ignore
    ]

    for variable, name in determined_pairs:
        riddle.addConstraint(lambda variable, name=name: variable == name, [variable])

    equal_variable_pairs = [
        ("second", match.group("color2")),
        match.group("color3", "drink1"),
        match.group("town1", "color5"),
        match.group("town3", "heirloom3"),
        match.group("town5", "drink4"),
        ("third", match.group("drink5")),
    ]

    for equal_variable_pair in equal_variable_pairs:
        riddle.addConstraint(AllEqualConstraint(), equal_variable_pair)

    def complex_constraint1(color3: str, color4: str, *seats: str) -> bool:
        """The lady in <color3> sat left of someone in <color4>."""
        return seats[-1] != color3 and seats[seats.index(color3) + 1] == color4

    riddle.addConstraint(
        complex_constraint1, [match.group("color3"), match.group("color4"), *seats]
    )

    def complex_constraint2(heirloom1: str, town2: str, *seats: str) -> bool:
        """When one of the dinner guests bragged about her
        <heirloom1>, the woman next to her said they were finer in <town2>,
        where she lived."""
        return any(
            seat == town2
            for _, seat in get_neighbouring_seats(seats.index(heirloom1), seats)
        )

    riddle.addConstraint(
        complex_constraint2, [match.group("heirloom1"), match.group("town2"), *seats]
    )

    def complex_constraint3(
        heirloom4: str, town4: str, drink2: str, *seats: str
    ) -> bool:
        """Someone else carried a valuable <heirloom4> and when she saw it,
        the visitor from <town4> next to her almost spilled her neighbor's
        <drink2>."""
        return any(
            seat1 == town4
            and any(
                seat2 == drink2
                for _, seat2 in get_neighbouring_seats(seat_number, seats)
            )
            for seat_number, seat1 in get_neighbouring_seats(
                seats.index(heirloom4), seats
            )
        )

    riddle.addConstraint(
        complex_constraint3,
        [match.group("heirloom4"), match.group("town4"), match.group("drink2"), *seats],
    )

    return riddle


def get_neighbouring_seats(
    seat_number: int, seats: Sequence[str]
) -> List[Tuple[int, str]]:
    if seat_number == 0:
        return [(1, seats[1])]
    elif seat_number == len(seats) - 1:
        return [(len(seats) - 1, seats[len(seats) - 1])]
    else:
        return [
            (seat_number - 1, seats[seat_number - 1]),
            (seat_number + 1, seats[seat_number + 1]),
        ]


if __name__ == "__main__":
    main()
