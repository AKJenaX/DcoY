with open('app.py', 'r', encoding='utf-8', errors='replace') as f:
    file_content = f.read()

# Replace use_container_width=True with width='stretch'
file_content = file_content.replace('use_container_width=True', "width='stretch'")

# Replace use_container_width=False with width='content'
file_content = file_content.replace('use_container_width=False', "width='content'")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(file_content)

print('Replacements completed successfully')
