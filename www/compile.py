# program for compile and minify html file with all css and js into one file
source_file = 'target.html'
output_file = 'index.html'

out = open(output_file, 'w')

with open(source_file) as f:
    while 1:
        line = f.readline()
        if line == '':
            break

        # change link
        if '"ws://192.168.4.1:80"' in line:
            line = line.replace('"ws://192.168.4.1:80"', '"ws://" + location.hostname + ":80"')
        # css style in
        if '<link href=' in line or '<script src=' in line:
            ext_file = line.replace(' ','').split('"')[1]
            # we have file name for it, so first insert <style> tags into the output file
            if '<script src=' in line:
                out.write('<script type="text/javascript">')
            else:
                out.write('<style type="text/css">')
            # and now read file and put each line on out
            with open(ext_file) as fe:
                while 1:
                    fe_line = fe.readline()
                    if fe_line == '':
                        break
                    out.write(fe_line)

            if '<script src=' in line:
                out.write('</script>')
            else:
                out.write('</style>')
        else:
            out.write(line)
out.close()
