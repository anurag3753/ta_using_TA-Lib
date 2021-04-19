
def get_stocks_set(filename):
    stocks_set = set()
    with open(filename, "r") as f:
        for stock in f:
            stock = stock.strip()
            stocks_set.add(stock)
    return stocks_set

universe_set = get_stocks_set("universe.txt")
invest_set = get_stocks_set("invest.txt")

# Get the stocks diff which are in universe.txt but not in invest.txt
diff = universe_set - invest_set
print(diff)
print(len(diff))

# covert the diff to a list and write in a file
diff_li = list(diff)
with open("temp_out.txt", "w") as f:
    for item in diff_li:
        f.write(item + "\n")
