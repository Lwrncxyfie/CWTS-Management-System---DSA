"""Activity 3 algorithms: Binary Search and Selection Sort.
Not used by the app yet. Phase 4 of WORK_PLAN.md plugs them into the tables and the student search."""


def binary_search(arr, key, get_key=lambda x: x):
    """Find record. Big O: O(log n).
    Return the index of `key` in a SORTED list, or -1 if not found.
    get_key extracts the value to compare (e.g. a record's name); the list must
    already be sorted by that same value."""
    lo, hi = 0, len(arr) - 1          # empty list -> loop never runs -> -1
    while lo <= hi:
        mid = (lo + hi) // 2
        mid_val = get_key(arr[mid])
        if mid_val == key:
            return mid
        if mid_val < key:
            lo = mid + 1              # search right half
        else:
            hi = mid - 1              # search left half
    return -1


def selection_sort(arr, get_key=lambda x: x, reverse=False):
    """Sort records. Big O: O(n^2). Return a NEW sorted list (original is not changed)."""
    result = list(arr)
    n = len(result)
    for i in range(n - 1):
        best = i                      # index of smallest (or largest)
        for j in range(i + 1, n):
            a, b = get_key(result[j]), get_key(result[best])
            if (a > b) if reverse else (a < b):
                best = j
        result[i], result[best] = result[best], result[i]
    return result
