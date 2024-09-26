
list1 = [1, 2, 3]
list2 = ['a', 'b', 'c']
result2 = [(idx, x, y) for idx, (x, y) in enumerate(zip(list1, list2))]
print(result2)
