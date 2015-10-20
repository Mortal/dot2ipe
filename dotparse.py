import re


def parse_params(p):
    pattern = r'([a-z]+)=([^",]+|"[^"]+")'
    matches = re.finditer(pattern, p)
    params = {}
    for mo in matches:
        k = mo.group(1)
        v = mo.group(2)
        if v.startswith('"'):
            v = v[1:-1].replace('\\\n', '')
        params[k] = v
    return params


def main():
    with open('deps-preservation.dot') as fp:
        s = fp.read()

    pattern = (
        r'(?P<u>[a-z0-9_]+)(?: -> (?P<v>[a-z0-9_]+))?' +
        r'\s*\[(?P<params>[^]]+)\];' +
        '')
    matches = re.finditer(pattern, s)

    glob = {}
    nodes = {}
    edge_lists = {}
    for mo in matches:
        u = mo.group('u')
        v = mo.group('v')
        p = mo.group('params')
        if v:
            edge_lists.setdefault(u, []).append((v, parse_params(p)))
        else:
            if u in ('graph', 'node'):
                glob[u] = parse_params(p)
            else:
                nodes[u] = parse_params(p)

    left, bottom, right, top = glob['graph']['bb'].split(',')
    print(('<layout paper="%s %s" origin="0 0" frame="%s %s" ' +
           'skip="0" crop="yes"/>') %
          (right, top, right, top))

    for u, e in edge_lists.items():
        for v, e_p in e:
            if e_p.get('style') == 'invis':
                continue

            a, *pos = e_p['pos'].split()
            pos.append(a[2:])
            print('<path stroke="black" arrow="normal/normal">')
            pos = [xy.replace(',', ' ') for xy in pos]
            pos[0] += ' m'
            pos[-1] += ' s'
            print('\n'.join(pos))
            print('</path>')

    for u, u_p in nodes.items():
        e = edge_lists.get(u, [])
        try:
            x, y = u_p['pos'].split(',')
        except KeyError:
            raise Exception("%s has no pos" % u)
        c = 'black'
        if 'color' in u_p:
            c = u_p['color']
        print(
            '<group matrix="%s 0 0 %s %s %s">\n' %
            (u_p['width'], u_p['height'], x, y) +
            '<path matrix="36 0 0 36 0 0" stroke="%s" fill="white">\n' % c +
            '-1 1 m\n' +
            '-1 -1 l\n' +
            '1 -1 l\n' +
            '1 1 l\n' +
            'h\n' +
            '</path>\n' +
            '<text transformations="translations" pos="0 0" stroke="black" ' +
            'type="label" halign="center" valign="center">' +
            u_p['label'].replace('_', '\\_') +
            '</text>' +
            '</group>')


if __name__ == "__main__":
    main()
