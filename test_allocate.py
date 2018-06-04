import allocate


def test_equal_group_size_when_match():
    allocation = allocate._random_allocation(things=range(10), resources=["first", "second"])
    assert all(x == 5 for x in allocation.groupby(allocation.values).size())


def test_last_group_is_smallest_when_one_thing_missing():
    allocation = allocate._random_allocation(things=range(20), resources=["first", "second", "third"])
    group_sizes = allocation.groupby(allocation.values).size()
    assert group_sizes["first"] == group_sizes["second"]
    assert group_sizes["first"] == 1 + group_sizes["third"]


def test_last_group_is_biggest_when_one_thing_too_much():
    allocation = allocate._random_allocation(things=range(22), resources=["first", "second", "third"])
    group_sizes = allocation.groupby(allocation.values).size()
    assert group_sizes["first"] == group_sizes["second"]
    assert group_sizes["third"] == 1 + group_sizes["first"]
