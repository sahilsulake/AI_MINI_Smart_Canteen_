class Order:
    def __init__(self, student, dish, prep_time, patience, arrival, seq=0):
        self.student = student
        self.dish = dish
        self.prep_time = int(prep_time)
        self.patience = int(patience)
        self.arrival = int(arrival)
        self.seq = seq

def run_strategy(orders, strategy):
    pending = sorted(orders, key=lambda o: (o.arrival, o.seq))
    time = 0
    served = []
    left = []

    while pending:
        available = [o for o in pending if o.arrival <= time]
        if not available:
            time = pending[0].arrival
            available = [o for o in pending if o.arrival <= time]

        if strategy == "FIFO":
            order = min(available, key=lambda o: (o.arrival, o.seq))
        elif strategy == "Greedy":
            order = min(available, key=lambda o: (o.prep_time, o.arrival, o.seq))
        elif strategy == "Patience":
            order = min(available, key=lambda o: (o.patience, o.arrival, o.seq))
        elif strategy == "Hybrid":
            order = min(available, key=lambda o: (o.prep_time + 0.5*o.patience, o.arrival, o.seq))
        else:
            order = available[0]

        start = time
        finish = start + order.prep_time
        deadline = order.arrival + order.patience

        if finish <= deadline:
            served.append({
                "student": order.student,
                "dish": order.dish,
                "prep": order.prep_time,
                "patience": order.patience,
                "arrival": order.arrival,
                "start": start,
                "finish": finish,
                "reason": "served"
            })
        else:
            left.append({
                "student": order.student,
                "dish": order.dish,
                "prep": order.prep_time,
                "patience": order.patience,
                "arrival": order.arrival,
                "tried_start": start,
                "tried_finish": finish,
                "reason": "patience_over"
            })

        time = finish
        pending.remove(order)

    # Next to serve
    if pending:
        if strategy=="FIFO":
            next_order = min(pending, key=lambda o: o.arrival)
        elif strategy=="Greedy":
            next_order = min(pending, key=lambda o: o.prep_time)
        elif strategy=="Patience":
            next_order = min(pending, key=lambda o: o.patience)
        else:
            next_order = min(pending, key=lambda o: o.prep_time + 0.5*o.patience)
        next_to_serve = {"student": next_order.student, "dish": next_order.dish, "prep": next_order.prep_time}
    else:
        next_to_serve = None

    return {"served": served, "left": left, "next_to_serve": next_to_serve}

def simulate_all_strategies(orders):
    strategies = ["FIFO", "Greedy", "Patience", "Hybrid"]
    results = {}
    for s in strategies:
        results[s] = run_strategy(orders, s)
    return results

def best_strategy(results):
    best = max(results.items(), key=lambda kv: len(kv[1]["served"]))
    return best[0], best[1]
