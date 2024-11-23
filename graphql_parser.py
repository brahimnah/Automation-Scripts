import json

# Function to load schema from file
def load_schema(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# Function to extract queries and mutations
def extract_queries_and_mutations(schema_json):
    schema_data = schema_json['data']['__schema']
    
    queries = []
    mutations = []
    
    for type_obj in schema_data['types']:
        if type_obj['name'] == 'Query':
            queries = type_obj['fields']
        elif type_obj['name'] == 'Mutation':
            mutations = type_obj['fields']
    
    return queries, mutations

# Format arguments for GraphQL query string
def format_argument(arg):
    arg_type = arg.get('type')
    
    # Traverse nested types (for NON_NULL, LIST, etc.)
    while arg_type and 'ofType' in arg_type:
        arg_type = arg_type['ofType']

    if not arg_type or not arg_type.get('name'):
        return None

    is_required = arg.get('type', {}).get('kind') == 'NON_NULL'
    arg_type_name = arg_type['name']
    return f"${arg['name']}: {arg_type_name}{'!' if is_required else ''}"

# Function to check if generated string has matching braces
def check_brace_balance(graphql_string):
    open_braces = graphql_string.count("{")
    close_braces = graphql_string.count("}")
    if open_braces != close_braces:
        print(f"Warning: Mismatched braces in the generated GraphQL string:\n{graphql_string}")
    return graphql_string

# Generate GraphQL query string with brace balance check
def generate_query_string(query):
    args = [format_argument(arg) for arg in query.get('args', [])]
    args = [arg for arg in args if arg is not None]
    args_str = ', '.join(args)

    fields = query.get('fields', [])
    field_names = " ".join([field['name'] for field in fields])

    query_string = f"query {query['name']}({args_str}) {{\n  {query['name']}({', '.join([arg['name'] for arg in query.get('args', [])])}) {{\n    {field_names}\n  }}\n}}"
    return check_brace_balance(query_string)

# Generate GraphQL mutation string with brace balance check
def generate_mutation_string(mutation):
    args = [format_argument(arg) for arg in mutation.get('args', [])]
    args = [arg for arg in args if arg is not None]
    args_str = ', '.join(args)

    fields = mutation.get('fields', [])
    field_names = " ".join([field['name'] for field in fields])

    mutation_string = f"mutation {mutation['name']}({args_str}) {{\n  {mutation['name']}({', '.join([arg['name'] for arg in mutation.get('args', [])])}) {{\n    {field_names}\n  }}\n}}"
    return check_brace_balance(mutation_string)

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
    schema_file = "./schema.json"  # Provide the correct path to your schema file
    schema_json = load_schema(schema_file)

    queries, mutations = extract_queries_and_mutations(schema_json)
    print_queries_and_mutations(queries, mutations)

if __name__ == "__main__":
    main()

