def extract_tags(mods):
    tags = set()
    for m in mods:
        for t in m.get("tags", []):
            tags.add(t["tag"])
    return tags

def build_by_category(mods, tags):
    out = {tag: [] for tag in tags}
    for m in mods:
        mid = m["publishedfileid"]
        for t in m.get("tags", []):
            if mid not in out[t["tag"]]:
                out[t["tag"]].append(mid)
    return out
