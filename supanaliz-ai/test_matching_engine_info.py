import inspect
import agents.matching_engine as me

print("Matching Engine file loaded from:")
print(inspect.getsourcefile(me))

print("\n=== First 50 lines of the file ===")
with open(inspect.getsourcefile(me), "r", encoding="utf-8") as f:
    for i in range(50):
        print(f.readline().rstrip())
