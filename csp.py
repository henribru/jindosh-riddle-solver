import itertools

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
items = ["snuff tin", "ring", "war medal", "bird pendant", "diamond"]
locations = ["Baleton", "Dunwall", "Dabokva", "Karnaca", "Fraeport"]
drinks = ["wine", "beer", "rum", "whiskey", "absinthe"]

jindosh_puzzle = Problem()
jindosh_puzzle.addVariables(
    list(itertools.chain(seats, colors, items, locations, drinks)), names
)

for variable_type in [seats, colors, items, locations, drinks]:
    jindosh_puzzle.addConstraint(AllDifferentConstraint(), variable_type)

determined = [
    ("blue", "Doctor Marcolla"),
    ("first", "Countess Contee"),
    ("ring", "Madam Natsiou"),
    ("rum", "Baroness Finch"),
    ("Fraeport", "Lady Winslow"),
]

for variable, name in determined:
    jindosh_puzzle.addConstraint(
        lambda variable, name=name: variable == name, [variable]
    )

equal_variables = [
    ("second", "purple"),
    ("red", "wine"),
    ("Baleton", "white"),
    ("Dunwall", "war medal"),
    ("Karnaca", "whiskey"),
    ("third", "absinthe"),
]

for equal in equal_variables:
    jindosh_puzzle.addConstraint(AllEqualConstraint(), equal)


def complex_constraint1(red, green, *seats):
    """The lady in red sat left of someone in green."""
    if seats[-1] == red:
        return False
    return seats[seats.index(red) + 1] == green


jindosh_puzzle.addConstraint(complex_constraint1, ["red", "green", *seats])


def get_neighbouring_seat(i, seats):
    if i == 0:
        return [(1, seats[1])]
    elif i == len(seats) - 1:
        return [(len(seats) - 1, seats[len(seats) - 1])]
    else:
        return [(i - 1, seats[i - 1]), (i + 1, seats[i + 1])]


def complex_constraint2(snuff_tin, baleton, *seats):
    """When one of the dinner guests bragged about her Snuff Tin,
    the woman next to her said they were finer in Baleton,
    where she lived."""
    return any(
        seat == baleton
        for _, seat in get_neighbouring_seat(seats.index(snuff_tin), seats)
    )


jindosh_puzzle.addConstraint(complex_constraint2, ["snuff tin", "Baleton", *seats])


def complex_constraint3(bird_pendant, dabokva, beer, *seats):
    """Someone else carried a valuable Bird Pendant and when she saw it,
    the visitor from Dabokva next to her almost spilled her neighbor's
    beer."""
    return any(
        seat == dabokva
        and any(seat == beer for _, seat in get_neighbouring_seat(j, seats))
        for j, seat in get_neighbouring_seat(seats.index(bird_pendant), seats)
    )


jindosh_puzzle.addConstraint(
    complex_constraint3, ["bird pendant", "Dabokva", "beer", *seats]
)
print(len(jindosh_puzzle.getSolutions()))
solution = jindosh_puzzle.getSolution()
ordered_names = [solution[seat] for seat in seats]
item_by_name = {solution[item]: item for item in items}
for name in ordered_names:
    print(f"{name}: {item_by_name[name]}")
