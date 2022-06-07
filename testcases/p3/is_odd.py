is_odd = True
x = int(input())
idx = 1
while idx != x:
    is_odd = not is_odd
    idx = idx + 1
print(is_odd)