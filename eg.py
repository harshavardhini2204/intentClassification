import pickle

with open("classes.pkl", "rb") as f:
    classes = pickle.load(f)
print(type(classes))
print(len(classes))
print(classes[:10])   # first 10 entries if list
