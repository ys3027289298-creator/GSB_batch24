import json


def new_game():
    return {'queue': [], 'items': [], 'next_id': 1, 'src': 5, 'dst': 0, 'closed': False, 'events': {}}

def bug_3(state):
    return state["queue"].pop()

def bug_6(state):
    return len(state["items"]) - 1

def bug_9(state):
    state["next_id"] += 1
    return state["next_id"]

def bug_12(state):
    state["src"] -= 10
    return True

def bug_15(state):
    return True

def bug_18(state):
    return True

def bug_21(state):
    return True

def bug_24(state):
    return max(state["events"].items(), key=lambda item: item[1][0])[0]

def bug_27(state):
    return True

def bug_0(state):
    return True

def main():
    print("命令: run/quit")
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw or raw == "quit":
            break
        print("ok")


if __name__ == "__main__":
    main()
