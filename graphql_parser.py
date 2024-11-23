import json

# Function to load schema from file
def load_schema(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# Function to extract queries and mutations
def extract_queries_and_mutations(schema_json):
    # We are directly using the introspection schema data
    # Extract the types
    schema_data = schema_json['data']['__schema']
    
    queries = []
    mutations = []
    
    # Extract Query and Mutation Types
    for type_obj in schema_data['types']:
        if type_obj['name'] == 'Query':
            queries = type_obj['fields']
        elif type_obj['name'] == 'Mutation':
            mutations = type_obj['fields']
    
    return queries, mutations

# Format arguments for GraphQL query string
def format_argument(arg):
    arg_type = arg.get('type', {})
    
    # If the argument type is None or empty, return None
    if not arg_type:
        return None

    # Traverse nested types (like NON_NULL, LIST)
    while 'ofType' in arg_type and arg_type['ofType'] is not None:
        arg_type = arg_type['ofType']

    # Get the argument type name
    arg_type_name = arg_type.get('name')

    # If no type name, return None (this may happen for custom types)
    if not arg_type_name:
        return None

    # Check if argument type is required (has a '!' in the name)
    is_required = '!' in arg_type_name
    return f"${arg['name']}: {arg_type_name.replace('!', '')}{'!' if is_required else ''}"

# Create GraphQL query string
def generate_query_string(query):
    args = [format_argument(arg) for arg in query.get('args', [])]
    # Filter out None values from args (in case some args are invalid or missing)
    args = list(filter(None, args))
    args_str = ', '.join(args)
    
    # Generate the query body (fields)
    return f"query {query['name']}({args_str}) {{\n  {query['name']}({', '.join([arg['name'] for arg in query.get('args', [])])}) {{\n    " + "\n    ".join([field['name'] for field in query.get('fields', [])]) + "\n  }}\n}}"

# Create GraphQL mutation string
def generate_mutation_string(mutation):
    args = [format_argument(arg) for arg in mutation.get('args', [])]
    # Filter out None values from args
    args = list(filter(None, args))
    args_str = ', '.join(args)
    
    # Generate the mutation body (fields)
    return f"mutation {mutation['name']}({args_str}) {{\n  {mutation['name']}({', '.join([arg['name'] for arg in mutation.get('args', [])])}) {{\n    " + "\n    ".join([field['name'] for field in mutation.get('fields', [])]) + "\n  }}\n}}"

# Print the generated query and mutation strings
def print_queries_and_mutations(queries, mutations):
    print("Queries:\n")
    for query in queries:
        print(generate_query_string(query))
        print("\n")

    print("\nMutations:\n")
    for mutation in mutations:
        print(generate_mutation_string(mutation))
        print("\n")

# Main function to load the schema and process it
def main():
    schema_file = "./schema.json"  # Provide the correct path to your schema
    schema_json = load_schema(schema_file)

    queries, mutations = extract_queries_and_mutations(schema_json)
    print_queries_and_mutations(queries, mutations)

if __name__ == "__main__":
    main()

