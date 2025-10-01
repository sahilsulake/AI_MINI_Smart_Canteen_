from flask import Flask, render_template, request, send_file, abort
import matplotlib.pyplot as plt
import io, base64, csv
from simulator import Order, simulate_all_strategies, best_strategy

app = Flask(__name__)
app.config["LAST_RESULTS"] = None

@app.route("/", methods=["GET","POST"])
def index():
    if request.method=="POST":
        try:
            num = int(request.form.get("num_orders"))
        except: num=1
        return render_template("orders.html", num_orders=num)
    return render_template("index.html")

@app.route("/simulate", methods=["POST"])
def simulate():
    num = int(request.form.get("num_orders"))
    orders = []
    for i in range(num):
        student = request.form.get(f"student{i}") or f"Student{i+1}"
        dish = request.form.get(f"dish{i}") or "Dish"
        prep = request.form.get(f"prep{i}") or 0
        patience = request.form.get(f"patience{i}") or 0
        arrival = request.form.get(f"arrival{i}") or 0
        orders.append(Order(student,dish,prep,patience,arrival,seq=i))

    results = simulate_all_strategies(orders)
    app.config["LAST_RESULTS"] = results
    best_strat, best_res = best_strategy(results)

    labels = list(results.keys())
    served_counts = [len(results[k]["served"]) for k in labels]
    left_counts = [len(results[k]["left"]) for k in labels]

    fig, ax = plt.subplots(figsize=(7,4))
    ax.bar(labels, served_counts, label="Served")
    ax.bar(labels, left_counts, bottom=served_counts, label="Left")
    ax.set_ylabel("Number of Students")
    ax.set_title("Strategy Comparison")
    ax.legend()
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)
    chart_b64 = base64.b64encode(buf.getvalue()).decode()

    return render_template("results_v5.html", chart_b64=chart_b64, best_strat=best_strat, best_res=best_res)

@app.route("/download_csv")
def download_csv():
    strat = request.args.get("strategy")
    results = app.config.get("LAST_RESULTS")
    if not results or strat not in results: return abort(404)
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["student","dish","prep","patience","arrival","status","start/ tried_start","finish/ tried_finish","reason"])
    for r in results[strat]["served"]:
        writer.writerow([r["student"], r["dish"], r["prep"], r["patience"], r["arrival"], "served", r["start"], r["finish"], r["reason"]])
    for r in results[strat]["left"]:
        writer.writerow([r["student"], r["dish"], r["prep"], r["patience"], r["arrival"], "not_served", r.get("tried_start",""), r.get("tried_finish",""), r["reason"]])
    mem = io.BytesIO()
    mem.write(out.getvalue().encode())
    mem.seek(0)
    return send_file(mem, mimetype="text/csv", download_name=f"{strat.lower()}_results.csv", as_attachment=True)

if __name__=="__main__":
    app.run(debug=True)
