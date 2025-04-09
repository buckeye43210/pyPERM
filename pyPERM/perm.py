#!/usr/bin/env python3

import sys
from collections import defaultdict

class Item:
    def __init__(self, name):
        self.name = name
        self.attributes = []

def parse_attribute_file(content):
    items = []
    all_full_attrs = set()
    current_item = None
    for line in content.splitlines():
        stripped = line.rstrip()
        if not stripped:
            continue
        indent_level = len(line) - len(line.lstrip('\t'))
        text = stripped.lstrip('\t')
        if indent_level == 0:
            continue
        elif indent_level == 1:
            current_item = Item(text)
            items.append(current_item)
        elif indent_level == 2 and current_item:
            full_text = text.strip()
            current_item.attributes.append(full_text)
            all_full_attrs.add(full_text)
    return items, all_full_attrs

def parse_category_file(content, all_full_attrs):
    full_categories = {}
    current_category = None
    for line in content.splitlines():
        stripped = line.rstrip()
        if not stripped:
            continue
        indent_level = len(line) - len(line.lstrip('\t'))
        text = stripped.lstrip('\t')
        if indent_level == 0:
            continue
        elif indent_level == 1:
            current_category = text
            full_categories[current_category] = []
        elif indent_level == 2 and current_category:
            full_text = text.strip()
            full_categories[current_category].append(full_text)
    for full_attr in all_full_attrs:
        found = False
        for cat_values in full_categories.values():
            if full_attr in cat_values:
                found = True
                break
        if not found:
            for item in [i for i in items if full_attr in i.attributes]:
                for cat in full_categories:
                    if any(v in item.attributes for v in full_categories[cat]):
                        full_categories[cat].append(full_attr)
                        break
                break
    return full_categories

def parse_priority_file(content):
    priorities = {"title": None, "groups": []}
    current_group = None
    for line in content.splitlines():
        stripped = line.rstrip()
        if not stripped:
            continue
        indent_level = len(line) - len(line.lstrip('\t'))
        text = stripped.lstrip('\t')
        if indent_level == 0:
            priorities["title"] = text
        elif indent_level == 1:
            current_group = {"title": text, "categories": []}
            priorities["groups"].append(current_group)
        elif indent_level == 2 and current_group:
            current_group["categories"].append(text.strip())
    return priorities

def build_decision_tree(items, full_categories, priorities):
    attr_map = defaultdict(list)
    for item in items:
        for value in item.attributes:
            attr_map[value].append(item)

    cat_to_full_values = {q: attrs for q, attrs in full_categories.items()}

    def filter_items(items, conditions):
        return [item for item in items if all(cond in item.attributes for cond in conditions.values())]

    def needs_splitting(parent_items, cat):
        if not cat:
            return False
        values = set()
        for item in parent_items:
            for attr in item.attributes:
                if attr in cat_to_full_values[cat]:
                    values.add(attr)
        return len(values) > 1

    def get_leaf_items(sub_branches):
        leaves = set()
        for branch in sub_branches:
            if not branch["sub_branches"]:
                leaves.add(branch["attr_value"])
            else:
                leaves.update(get_leaf_items(branch["sub_branches"]))
        return leaves

    def build_sub_branches(parent_items, conditions, remaining_cats, top_category):
        if len(parent_items) == 1:
            return [{"attr_value": parent_items[0].name, "sub_branches": []}]
        if not remaining_cats:
            return [{"attr_value": item.name, "sub_branches": []} for item in parent_items]
        
        current_cat = remaining_cats[0]
        sub_values = cat_to_full_values[current_cat]
        sub_branches = []
        seen_values = set()
        
        if not needs_splitting(parent_items, current_cat):
            return build_sub_branches(parent_items, conditions, remaining_cats[1:], top_category)
        
        for full_value in sub_values:
            if full_value in seen_values:
                continue
            sub_items = filter_items(parent_items, conditions | {current_cat: full_value})
            if sub_items:
                sub_branch = {"attr_value": full_value, "sub_branches": []}
                sub_branch["sub_branches"] = build_sub_branches(sub_items, conditions | {current_cat: full_value}, remaining_cats[1:], top_category)
                sub_branches.append(sub_branch)
                seen_values.add(full_value)
        
        # Simplify with ELSE: when not top category and branches lead to identical outcomes
        if len(sub_branches) > 1 and current_cat != top_category:
            leaf_counts = defaultdict(list)
            for branch in sub_branches:
                leaves = get_leaf_items(branch["sub_branches"])
                leaf_counts[tuple(sorted(leaves))].append(branch)
            
            new_branches = []
            consolidated = set()
            for leaf_tuple, branches in leaf_counts.items():
                if len(branches) > 1:
                    leaf_set = set(leaf_tuple)
                    if len(leaf_set) == 1:  # Single item across multiple branches
                        item_name = leaf_tuple[0]
                        if item_name not in consolidated:
                            new_branches.append({"attr_value": "ELSE:", "sub_branches": [{"attr_value": item_name, "sub_branches": []}]})
                            consolidated.add(item_name)
                    else:
                        new_branches.extend(branches)
                else:
                    new_branches.extend(branches)
            sub_branches = new_branches
        
        if not sub_branches and parent_items:
            return [{"attr_value": item.name, "sub_branches": []} for item in parent_items]
        return sub_branches

    tree = {"title": priorities["title"], "groups": []}
    for group in priorities["groups"]:
        group_tree = {"title": group["title"], "branches": []}
        tree["groups"].append(group_tree)
        
        top_cat = group["categories"][0]
        top_values = cat_to_full_values[top_cat]
        for full_value in top_values:
            items_with_value = attr_map[full_value]
            if items_with_value:
                branch = {"attr_value": full_value, "sub_branches": []}
                branch["sub_branches"] = build_sub_branches(items_with_value, {top_cat: full_value}, group["categories"][1:], top_cat)
                group_tree["branches"].append(branch)

    return tree

def print_text_output(tree):
    def print_branch(node, indent=0):
        tabs = "\t" * indent
        print(f"{tabs}{node['attr_value']}")
        for sub_branch in node["sub_branches"]:
            print_branch(sub_branch, indent + 1)

    print(f"{tree['title']}")
    for group in tree["groups"]:
        print(f"\t{group['title']}")
        for branch in group["branches"]:
            print_branch(branch, 2)
    print()

def main():
    if len(sys.argv) != 4:
        print("Usage: python perm.py attr_file cat_file pri_file", file=sys.stderr)
        sys.exit(1)

    attr_file, cat_file, pri_file = sys.argv[1:4]

    with open(attr_file, 'r') as f:
        attribute_content = f.read()
    with open(cat_file, 'r') as f:
        category_content = f.read()
    with open(pri_file, 'r') as f:
        priority_content = f.read()

    items, all_full_attrs = parse_attribute_file(attribute_content)
    full_categories = parse_category_file(category_content, all_full_attrs)
    priorities = parse_priority_file(priority_content)

    tree = build_decision_tree(items, full_categories, priorities)
    print_text_output(tree)

if __name__ == "__main__":
    main()
