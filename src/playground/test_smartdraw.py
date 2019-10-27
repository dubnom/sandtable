import re
from SmartDraw import SmartDraw
from Sand import DATA_PATH

if __name__ == '__main__':
    chains = [
        [(3., 3.), (9., 11.), (7., 1.), (3., 3.)],
        [(15., 15.), (18., 15.), (18., 18.), (15., 18.), (15., 15.)],
        [(19., 16.), (20., 16.), (20., 17.), (19., 17.), (19., 16.)],
        [(10., 10.), (25., 10.), (25., 20.), (10., 20.), (10., 10.)],
        [(27, 3), (29, 11), (28, 1), (27, 3)],
        [(1, 2), (2, 2), (1, 18)],
    ]

    # Read the last gcode file, remove scan lines and scan line motion
    # and convert into chains
    import re
    pattern = re.compile('G01 X([0-9,\\\\.]+)Y(.+)$')
    chains = []
    with open('../%sgcode.ngc' % DATA_PATH, 'r') as f:
        lines = f.readlines()
        chain = []
        for s in lines[2:-1]:
            if s.startswith("% Chain"):
                if len(chain):
                    chains.append(chain)
                    chain = []
            elif s.startswith("G01"):
                xs, ys = pattern.match(s).groups()
                chain.append((float(xs), float(ys)))
        if len(chain):
            chains.append(chain)

    del(chains[0])
    del(chains[-1])
    for chain in chains:
        del(chain[0])
        del(chain[-1])

    SmartDraw(chains, 30., 20., 1.)
