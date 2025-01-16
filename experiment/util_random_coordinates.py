import math
import random


def get_random_coordinate(lower_bound: float, upper_bound: float) -> tuple:
    """
    Generates a random coordinate (X, Y) within the given bounds.

    Parameters:
        lower_bound (int or float): The lower bound for X and Y.
        upper_bound (int or float): The upper bound for X and Y.

    Returns:
        tuple: A random coordinate (X, Y).
    """
    if lower_bound > upper_bound:
        raise ValueError("Lower bound must be less than or equal to upper bound.")

    x = random.randint(lower_bound, upper_bound)
    y = random.randint(lower_bound, upper_bound)
    return (x, y)


def get_distant_coordinate(
    ref_x: int, ref_y: int, lower_bound: int, upper_bound: int, min_distance: float
) -> tuple:
    """
    Repeatedly generates a random coordinate until it's at least `min_distance` away
    from the given coordinate (x, y).

    Parameters:
        ref_x (int): X-coordinate of the reference point.
        ref_y (int): Y-coordinate of the reference point.
        lower_bound (int): Lower bound for random coordinates.
        upper_bound (int): Upper bound for random coordinates.
        min_distance (float): Minimum required distance.

    Returns:
        tuple: A random coordinate (X', Y') at least `min_distance` away.
    """
    while True:
        random_coord = get_random_coordinate(
            lower_bound=lower_bound, upper_bound=upper_bound
        )
        distance = math.sqrt(
            (random_coord[0] - ref_x) ** 2 + (random_coord[1] - ref_y) ** 2
        )
        if distance >= min_distance:
            return random_coord


def main():
    """
    Simple demonstration of the get_random_coordinate() function.
    """
    print("Simple demonstration of get_random_coordinate()")
    print(get_random_coordinate(lower_bound=100, upper_bound=500))
    print(get_random_coordinate(lower_bound=100, upper_bound=500))

    print(
        "Simple demonstration of generate_distant_coordinate(). Note that every coordinate is at least 50 units away"
    )
    ref_coordinate = get_random_coordinate(lower_bound=100, upper_bound=500)
    print(
        get_distant_coordinate(
            ref_x=ref_coordinate[0],
            ref_y=ref_coordinate[1],
            lower_bound=100,
            upper_bound=500,
            min_distance=50,
        )
    )
    print(
        get_distant_coordinate(
            ref_x=ref_coordinate[0],
            ref_y=ref_coordinate[1],
            lower_bound=100,
            upper_bound=500,
            min_distance=50,
        )
    )
    print(
        get_distant_coordinate(
            ref_x=ref_coordinate[0],
            ref_y=ref_coordinate[1],
            lower_bound=100,
            upper_bound=500,
            min_distance=50,
        )
    )
    print(
        get_distant_coordinate(
            ref_x=ref_coordinate[0],
            ref_y=ref_coordinate[1],
            lower_bound=100,
            upper_bound=500,
            min_distance=50,
        )
    )


if __name__ == "__main__":
    main()
