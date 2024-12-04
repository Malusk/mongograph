import re
import json
from pymongo import MongoClient

def parse_cypher_to_json(input_file="grafoEjemplos", output_file="output.json"):
    
    MONGO_URI = 'mongodb+srv://admin_demo:TM0SOlhMZTpecJeR@cluster0.z05nk.mongodb.net/'
    DATABASE_NAME = 'matrix_database'
    # Read Cypher text from file
    try:
        with open(input_file, 'r') as file:
            cypher_text = file.read()
    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
        return
    
    # Connect to MongoDB
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    
    # Create or clear collections
    nodes_collection = db['nodes']
    relationships_collection = db['relationships']
    
    # Clear existing data
    nodes_collection.delete_many({})
    relationships_collection.delete_many({})
    
    # Regular expressions for parsing
    node_pattern = r'CREATE \((\w+):(\w+) \{([^}]+)\}\)'
    relationship_pattern = r'\((\w+)\)-\[:(\w+) ?(?:\{[^}]+\})?\]->\((\w+)\)'
    
    # Parse and insert nodes
    node_matches = re.findall(node_pattern, cypher_text)
    nodes_to_insert = []
    
    for match in node_matches:
        node_id, node_type, props_str = match
        props = dict(re.findall(r'(\w+):([^,}]+)', props_str))
        
        # Convert numeric values
        for key in props:
            try:
                props[key] = int(props[key].strip("'"))
            except ValueError:
                props[key] = props[key].strip("'")
        
        # Add _id and type to props
        node_doc = {
            '_id': node_id,
            'type': node_type,
            **props
        }
        
        nodes_to_insert.append(node_doc)
    
    # Bulk insert nodes
    if nodes_to_insert:
        nodes_collection.insert_many(nodes_to_insert)
    
    # Parse and insert relationships
    rel_matches = re.findall(relationship_pattern, cypher_text)
    relationships_to_insert = []
    
    for match in rel_matches:
        source, rel_type, target = match
        
        # Prepare relationship document
        rel_doc = {
            'from': source,
            'to': target,
            'type': rel_type
        }
        
        # Add roles if present in relationship (for ACTED_IN)
        role_pattern = rf'\(({re.escape(source)})\)-\[:ACTED_IN \{{roles:\[\'([^\']+)\'\]}}\]->\(({re.escape(target)})\)'
        role_match = re.search(role_pattern, cypher_text)
        
        if role_match:
            rel_doc['roles'] = [role_match.group(2)]
        
        relationships_to_insert.append(rel_doc)
    
    # Bulk insert relationships
    if relationships_to_insert:
        relationships_collection.insert_many(relationships_to_insert)
    
    # Print summary
    print(f"Imported {len(nodes_to_insert)} nodes")
    print(f"Imported {len(relationships_to_insert)} relationships")
    
    # Close MongoDB connection
    client.close()

# Automatically execute the script
if __name__ == "__main__":
    parse_cypher_to_json()
