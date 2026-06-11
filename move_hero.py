import sys
with open(r'c:\Users\Sneh Suman\OneDrive\Desktop\PROJ\streamlit_app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

hero_start = -1
hero_end = -1
render_line = -1

for i, line in enumerate(lines):
    if line.startswith('HERO_HTML = '):
        hero_start = i
    elif line.startswith('"""') and hero_start != -1 and hero_end == -1 and i > hero_start:
        hero_end = i
    elif line.startswith('components.html(HERO_HTML'):
        render_line = i

if hero_start != -1 and hero_end != -1 and render_line != -1:
    hero_block = lines[hero_start:hero_end+1]
    render_block = [lines[render_line]]
    
    del lines[render_line]
    # Re-calculate indices since we deleted a line that might be after
    if render_line < hero_start:
        hero_start -= 1
        hero_end -= 1
        
    del lines[hero_start:hero_end+1]
    
    insert_idx = 0
    for i, line in enumerate(lines):
        if line.strip() == ')' and 'st.set_page_config' in "".join(lines[max(0, i-5):i]):
            insert_idx = i + 1
            break
            
    lines = lines[:insert_idx] + ['\n'] + hero_block + ['\n'] + render_block + ['\n'] + lines[insert_idx:]
    
    with open(r'c:\Users\Sneh Suman\OneDrive\Desktop\PROJ\streamlit_app.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("SUCCESS")
else:
    print(f"FAILED {hero_start} {hero_end} {render_line}")
