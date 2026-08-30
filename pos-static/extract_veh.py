src="/tmp/full_restored.sql"
out="/tmp/veh_only.sql"
state=0
with open(src) as f, open(out, "w") as o:
    for line in f:
        if line.startswith('COPY public."tabVehicle" ('):
            state = 1
            o.write(line)
            continue
        if state == 1:
            o.write(line)
            if line.strip() == "\\.":
                state = 0
print("extracted tabVehicle COPY block")
