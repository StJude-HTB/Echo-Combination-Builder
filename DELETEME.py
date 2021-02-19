import string, warnings, re, itertools, os


def show_list(header, l):
    print(header)
    [print(li.strip()) for li in l]
    print("\n")
    return

def sort_transfers(transfers, priority="source"):
    if(priority not in ["source", "destination"]):
        raise Exception("Invalid Argument: Argument priority must be one of 'source' or 'destination'")
    else:
        show_list("INPUT:", transfers)
        n = [transfers[0]]
        x = transfers[1:]
        match_pattern1 = re.compile(r'^(?P<sn>[a-zA-Z0-9_-]+),(?P<sr>[0-9]{1,2}),(?P<sc>[0-9]{1,2}),(?P<dn>[a-zA-Z0-9_-]+),(?P<dr>[0-9]{1,2}),(?P<dc>[0-9]{1,2}),(?P<tv>[0-9\.]+),(?P<tn>.+)$')
        sorting_dict = dict()
        for t in x:
            m = match_pattern1.match(t)
            if(m):
                d = m.groupdict()
                if(priority == "source"):
                    s = d["sn"] + d["dn"] + ("0" + d["sr"])[-2:] + ("0" + d["sc"])[-2:] + ("0" + d["dr"])[-2:] + ("0" + d["dc"])[-2:]
                    sorting_dict[s] = t
                if(priority == "destination"):
                    s = d["sn"] + d["dn"] + ("0" + d["dr"])[-2:] + ("0" + d["dc"])[-2:] + ("0" + d["sr"])[-2:] + ("0" + d["sc"])[-2:]
                    sorting_dict[s] = t
        refs = list(sorting_dict.keys())
        refs.sort()
        [n.append(sorting_dict[k]) for k in refs]
        show_list("SORTED:", n)
    return n