def is_true(x):
    return x == True

def true_fun():
    return True

if is_true(bool(input())):
    print(true_fun())
else:
    print(not true_fun())