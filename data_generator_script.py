import random, csv, datetime
random.seed(42)

CITIES = ["Rivermouth","Northgate","Lakeview","Eastport","Westbridge","Hillcrest"]
ZONES_BY_CITY = {
    "Rivermouth": ["Central Plaza","Riverside","Old Town","Tech Park","Market Square","Uptown","Harbor District","Downtown"],
    "Northgate": ["Green Park","University Area","Garden City","Industrial Zone"],
    "Lakeview": ["Lakeside","Hilltop","Sunset Boulevard","Cultural Quarter"],
    "Eastport": ["Business Bay","Airport Road","Stadium Area"],
    "Westbridge": ["Residential Heights","West Common","Millbrook"],
    "Hillcrest": ["Hill Gardens","North Ridge"],
}
ALL_ZONES = [z for zs in ZONES_BY_CITY.values() for z in zs]

CHAIN_NAMES = ["Golden Wok","Crispy Bucket Chicken","Urban Pizza Co","Spice Route Kitchen",
 "Noodle House Express","Burger Junction","Sizzling Grill House","Curry Leaf Kitchen",
 "Milk & Honey Bakery","Fresh Greens Salad Bar","Taco Fiesta","Sushi Circle",
 "Kabab Corner","Steam Bowl Asian Kitchen","Firehouse Wings","Cheesy Crust Pizza",
 "Rice & Spice","Grand Biryani House","Coastal Seafood Grill","Sweet Tooth Desserts",
 "Rolls & Wraps Co","Charcoal Chicken House","Pasta Palace","Morning Brew Cafe",
 "Royal Kebab House","The Breakfast Table","Green Bowl Healthy Eats","Smokehouse BBQ",
 "Lotus Garden Chinese","Cloud Nine Bakery"]

CUISINES = ["Fast Food","Chicken","Pizza","Chinese","Burger","Bakery","Healthy",
 "Biryani & Rice","Seafood","Desserts","Coffee & Tea","Kebab","BBQ","Salad","Breakfast"]

RESTAURANT_TYPES = ["restaurant","shop","mart"]

FAKE_FIRST = ["Alex","Jordan","Sam","Taylor","Casey","Riley","Jamie","Morgan","Drew","Avery",
 "Reese","Cameron","Skyler","Rowan","Quinn","Harper","Emerson","Dakota","Finley","Hayden"]
FAKE_LAST = ["Morgan","Lee","Rivera","Brooks","Kim","Chen","Patel","Diaz","Kelly","Singh",
 "Osei","Nguyen","Foster","Bennett","Hayes","Cole","Reyes","Price","Ward","Nash"]

def fake_person(used):
    while True:
        name = f"{random.choice(FAKE_FIRST)} {random.choice(FAKE_LAST)}"
        if name not in used:
            used.add(name)
            return name

used_names = set()
ACCOUNT_MANAGERS = [fake_person(used_names) for _ in range(10)]
OPS_STAFF = [fake_person(used_names) for _ in range(10)]
OPS_MANAGERS = [fake_person(used_names) for _ in range(3)]

PAYMENT_GATEWAYS = ["cash","walletA","walletB","bankA","bankB","bankC","bankD","cardgw"]
PAYMENT_METHODS = ["cash","online"]
ORDER_STATUSES = ["delivered","cancelled","not_delivered","restaurant_rejected",
 "customer_received","restaurant_accepted","placed"]
ORDER_STATUS_WEIGHTS = [70,8,5,4,4,4,5]
ORDER_TYPES = ["delivery","pickup","flower"]
ORDER_TYPE_WEIGHTS = [90,8,2]

# ---------- Restaurant master ----------
N_RESTAURANTS = 450
restaurants = []
for i in range(N_RESTAURANTS):
    branch_id = 10000 + i
    primary_id = 2000 + (i % 150)
    chain = random.choice(CHAIN_NAMES)
    city = random.choices(CITIES, weights=[40,15,15,12,10,8])[0]
    zone = random.choice(ZONES_BY_CITY[city])
    cuisines = ", ".join(random.sample(CUISINES, k=random.randint(2,4)))
    restaurants.append({
        "restaurant_branch_id": branch_id,
        "restaurant_branch_name": f"{chain} - {zone}",
        "restaurant_primary_id": primary_id,
        "restaurant_primary_name": chain,
        "restaurant_zone_id": ALL_ZONES.index(zone)+1,
        "restaurant_zone_name": zone,
        "city_name": city,
        "cuisine_name": cuisines,
        "commission_pct": round(random.uniform(12,25),1),
        "enabled_disabled": random.choices(["enabled","disabled"], weights=[92,8])[0],
        "restaurant_onboard_date": (datetime.date(2023,1,1)+datetime.timedelta(days=random.randint(0,900))).isoformat(),
        "is_credit": random.choice(["yes","no"]),
        "delivery_by_partner": random.choice([True, False]),
        "restaurant_type": random.choices(RESTAURANT_TYPES, weights=[85,10,5])[0],
        "chain": chain,
        "account_manager": random.choice(ACCOUNT_MANAGERS),
        "cuisine": cuisines.split(",")[0].strip(),
        "ops_staff": random.choice(OPS_STAFF),
        "ops_manager": random.choice(OPS_MANAGERS),
        "status": random.choices(["OPEN","CLOSED","Temporarily Closed"], weights=[88,7,5])[0],
    })

with open("/home/claude/build/data/sample_restaurant_master.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(restaurants[0].keys()))
    w.writeheader()
    w.writerows(restaurants)

# ---------- Orders ----------
N_ORDERS = 25000
start_date = datetime.datetime(2026,1,1)
days_span = 150

def sample_hour():
    # weighted toward lunch (12-14) and dinner (19-22) peaks
    buckets = list(range(24))
    weights = [1,1,1,1,1,1,2,3,4,5,6,10,14,10,6,5,6,8,10,14,16,12,6,3]
    return random.choices(buckets, weights=weights)[0]

def sample_amount():
    val = random.lognormvariate(5.9, 0.55)
    return round(min(max(val, 80), 6000), 2)

riders = [f"RDR-{i:04d}" for i in range(1, 900)]

fieldnames = ["Order ID","Order Date","Restaurant Branch ID","Restaurant Name","Customer ID",
 "Rider ID","Order Status","Order Type","Total Amount","Branch Zone","Delivery Zone",
 "Payment Method","Payment Gateway","Payment Status","Delivery Charge","Discount Amount",
 "Promo Code","Restaurant Commission","Platform Subsidy","Restaurant Subsidy Share",
 "Rider Earning","Avg Delivery Time Min","Delivery Status","Month Name","Date"]

with open("/home/claude/build/data/sample_orders.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    for i in range(N_ORDERS):
        r = random.choice(restaurants)
        d = start_date + datetime.timedelta(days=random.randint(0,days_span))
        hh = sample_hour()
        mm = random.randint(0,59)
        ss = random.randint(0,59)
        order_dt = d.replace(hour=hh, minute=mm, second=ss)
        status = random.choices(ORDER_STATUSES, weights=ORDER_STATUS_WEIGHTS)[0]
        amount = sample_amount()
        commission = round(amount * r["commission_pct"]/100, 2)
        subsidy = round(random.uniform(0, amount*0.08), 2) if random.random() < 0.35 else 0
        w.writerow({
            "Order ID": f"ORD{100000+i}",
            "Order Date": order_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "Restaurant Branch ID": r["restaurant_branch_id"],
            "Restaurant Name": r["restaurant_branch_name"],
            "Customer ID": f"CUST{random.randint(1,9000):05d}",
            "Rider ID": random.choice(riders) if status not in ("placed",) else "",
            "Order Status": status,
            "Order Type": random.choices(ORDER_TYPES, weights=ORDER_TYPE_WEIGHTS)[0],
            "Total Amount": amount,
            "Branch Zone": r["restaurant_zone_name"],
            "Delivery Zone": random.choice(ALL_ZONES),
            "Payment Method": random.choices(PAYMENT_METHODS, weights=[55,45])[0],
            "Payment Gateway": random.choice(PAYMENT_GATEWAYS),
            "Payment Status": random.choices(["paid","pending","failed","refunded"], weights=[90,4,3,3])[0],
            "Delivery Charge": random.choice([0,20,30,40,50]),
            "Discount Amount": random.choice([0,0,0,20,30,50,100]),
            "Promo Code": random.choice(["", "", "", "WELCOME10","SAVE20","FREESHIP"]),
            "Restaurant Commission": commission,
            "Platform Subsidy": subsidy,
            "Restaurant Subsidy Share": round(subsidy*0.3,2),
            "Rider Earning": random.choice([40,50,60,70,80]),
            "Avg Delivery Time Min": random.randint(15,55),
            "Delivery Status": status == "delivered",
            "Month Name": order_dt.strftime("%B"),
            "Date": order_dt.strftime("%Y-%m-%d"),
        })

print("Restaurants:", len(restaurants), "Orders:", N_ORDERS)
