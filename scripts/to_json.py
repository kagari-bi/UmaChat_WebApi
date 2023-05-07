import json

def parse_line(line):
    data = {}
    parts = line.strip().split('：')

    if len(parts) == 2:
        key, value = parts
        if ' ' not in value:
            data[key] = {"动作名称": value.strip()}
        else:
            value_parts = value.strip().split()
            action_name = value_parts[0].strip()
            attr_parts = value_parts[1].split('=')
            attr_key, attr_value = attr_parts[0].strip(), attr_parts[1].strip()
            data[key] = {
                "动作名称": action_name,
                "形态键": attr_key,
                "权重": float(attr_value)
            }
    return data

def process_file(file_path):
    data = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            data.update(parse_line(line))
    return data

def save_to_json(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    file_path = "美妙姿势动作映射表.txt"
    output_file = "output.json"

    data = process_file(file_path)
    save_to_json(data, output_file)
