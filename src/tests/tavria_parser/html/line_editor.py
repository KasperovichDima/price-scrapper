source = '/home/kasper/Documents/projects/monitoring/src/tests/tavria_parser/html/del_it.html'
target = '/home/kasper/Documents/projects/monitoring/src/tests/tavria_parser/html/fast_food.html'
with open(source, 'r') as source_file:
    with open(target, 'w') as target_file:
        for line in source_file.readlines():
            str_line = str(line)
            if str_line.startswith('<a href="/product/'):
                if str_line.endswith('</a>\n'):
                    target_file.write(line)