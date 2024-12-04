from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import json

app = Flask(__name__)

# MongoDB configuration
MONGO_URI = 'mongodb+srv://admin_demo:TM0SOlhMZTpecJeR@cluster0.z05nk.mongodb.net/'
DATABASE_NAME = 'matrix_database'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute_pipeline():
    node_id = request.form.get('node_id')  # Get _id value from the form
    depth = request.form.get('depth')  # Get depth value from the form

    # Validate depth input
    try:
        depth = int(depth)
    except ValueError:
        return jsonify({"error": "Depth must be an integer."}), 400

    # Connect to MongoDB
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db['nodes']

    # Fetch the input document for reference
    input_doc = collection.find_one({"_id": node_id})
    if not input_doc:
        return jsonify({"error": f"Node with _id '{node_id}' not found."}), 404

    if input_doc.get("type") == "Movie":
        to_field = "from"
        from_field = "to"
    else:
        to_field = "to"
        from_field = "from"

    # Define the aggregation pipeline
    pipeline = [
        {"$match": {"_id": node_id}},  # Dynamically match the _id
        {"$graphLookup": {
            "from": "relationships",
            "startWith": "$_id",
            "connectFromField": to_field,
            "connectToField": from_field,
            "as": "relationships",
            "maxDepth": depth
        }},
        {"$lookup": {
            "from": "nodes",
            "localField": "relationships.from",
            "foreignField": "_id",
            "as": "fromNodes"
        }},
        {"$lookup": {
            "from": "nodes",
            "localField": "relationships.to",
            "foreignField": "_id",
            "as": "toNodes"
        }},
        {"$project": {
            "nodes": {
                "$map": {
                    "input": {"$setUnion": ["$fromNodes", "$toNodes"]},
                    "as": "node",
                    "in": {
                        "id": "$$node._id",
                        "label": {
                            "$cond": [
                                {"$eq": ["$$node.type", "Movie"]},
                                "$$node.title",
                                "$$node.name"
                            ]
                        },
                        "type": "$$node.type",
                        "properties": {
                            "title": "$$node.title",
                            "name": "$$node.name",
                            "released": "$$node.released",
                            "tagline": "$$node.tagline",
                            "born": "$$node.born"
                        }
                    }
                }
            },
            "links": {
                "$map": {
                    "input": "$relationships",
                    "as": "rel",
                    "in": {
                        "source": "$$rel.from",
                        "target": "$$rel.to",
                        "type": "$$rel.type",
                        "roles": "$$rel.roles"
                    }
                }
            }
        }}
    ]

    # Execute the pipeline
    try:
        results = list(collection.aggregate(pipeline))
    except Exception as e:
        return jsonify({"error": str(e)})

    # Export the results to a file
    try:
        with open('visualizer.json', 'w') as outfile:
            json.dump(results, outfile, indent=4)
    except Exception as e:
        return jsonify({"error": f"Failed to write to file: {str(e)}"})

    # Close MongoDB connection
    client.close()

    return jsonify({
        "input_document": input_doc,
        "output_document": results
    })

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)