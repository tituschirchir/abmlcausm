import random


class ForecastRule:
    def __init__(self, rule_string, a, b, accuracy):
        self.rule_string = rule_string
        self.a = a
        self.b = b
        self.accuracy = accuracy

    def __str__(self):
        return "Rule: {}, a: {}, b: {}, accuracy: {}".format(self.rule_string,
                                                             str(round(self.a, 2)), str(round(self.b, 2)),
                                                             str(round(self.accuracy, 2)))

    def match_to_market(self, model):
        for idx, ch in enumerate(self.rule_string):
            if ch != "#" and ch != model.stock.rule_string[idx]: return False
        return True


def mutate_rule(rule):
    new_rule = rule
    new_string = ""
    for idx, ch in enumerate(new_rule.rule_string):
        if random.random() < 0.03:
            if ch == "0":
                new_string += "#" if random.random() < 2. / 3. else "1"
            elif ch == "1":
                new_string += "#" if random.random() < 2. / 3. else "0"
            else:
                new_string += "1" if random.random() < 0.5 else "0"
        else:
            new_string += ch
    new_rule.rule_string = new_string
    p_a = random.random()
    if p_a < 0.2:
        new_rule.a = random.random() * 0.5 + 0.7  # range from 0.7 to 1.2
    elif p_a < 0.4:
        new_rule.a += ((random.random() - 0.5) / 10) * 0.5

    p_b = random.random()
    if p_b < 0.2:
        new_rule.b = random.random() * 29. - 10.
    elif p_b < 0.4:
        new_rule.b += ((random.random() - 0.5) / 10) * 29

    return new_rule


def crossover_rules(rule_1, rule_2):
    pass


def generate_random_rule():
    string = ""
    for c in range(10):
        r = random.random()
        string += "0" if r < 0.05 else ("1" if r < 0.10 else "#")
    string += "10"
    a = random.random() * 0.5 + 0.7  # range from 0.7 to 1.2
    b = random.random() * 29. - 10.
    return ForecastRule(string, a, b, 4.)


rule = generate_random_rule()
print(rule)
[print(mutate_rule(rule)) for i in range(10)]
