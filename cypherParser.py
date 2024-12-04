import re
import json

def parse_cypher_to_json(input_file="grafoEjemplos", output_file="output.json"):
    # Read Cypher text from file
    try:
        with open(input_file, 'r') as file:
            cypher_text = file.read()
    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
        return
    
    # Initialize data structures
    nodes = {}
    links = []
    
    # Regular expressions for parsing
    node_pattern = r'CREATE \((\w+):(\w+) \{([^}]+)\}\)'
    relationship_pattern = r'\((\w+)\)-\[:(\w+) ?(?:\{[^}]+\})?\]->\((\w+)\)'
    
    # Parse nodes first
    node_matches = re.findall(node_pattern, cypher_text)
    for match in node_matches:
        node_id, node_type, props_str = match
        props = dict(re.findall(r'(\w+):([^,}]+)', props_str))
        
        # Convert numeric values
        for key in props:
            try:
                props[key] = int(props[key].strip("'"))
            except ValueError:
                props[key] = props[key].strip("'")
        
        nodes[node_id] = {
            "id": node_id,
            "label": props.get("name", props.get("title", node_id)),
            "type": node_type,
            "properties": props
        }
    
    # Parse relationships
    rel_matches = re.findall(relationship_pattern, cypher_text)
    for match in rel_matches:
        source, rel_type, target = match
        
        # Ensure both source and target nodes exist
        if source not in nodes or target not in nodes:
            print(f"Warning: Skipping link from {source} to {target} - node not found")
            continue
        
        links.append({
            "source": source,
            "target": target,
            "type": rel_type
        })
    
    # Prepare D3.js compatible JSON
    result = {
        "nodes": list(nodes.values()),
        "links": links
    }
    
    # Output to file
    try:
        with open(output_file, 'w') as file:
            json.dump(result, file, indent=2)
        print(f"JSON saved to {output_file}")
    except Exception as e:
        print(f"Error writing to file: {e}")
    
    return result

# Automatically execute the script
if __name__ == "__main__":
    parse_cypher_to_json()