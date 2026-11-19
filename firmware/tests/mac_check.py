#!/usr/bin/env python3
"""Build the Cal-V2 pulse compiler on a Mac and check it (Python 3, clang++ with Rosetta; nothing here runs on the lab PC).

    python3 firmware/tests/mac_check.py [--lab DAYFOLDER] [--gui FREQ_SCAN_GUI_REPO]

Builds firmware/NewDDS2-Cooling2.0-Cal-V2 for x86_64 in a temporary folder (stubs/ stands in for windows.h and
NIDAQmx.h: the compiler never touches the card) and checks:

  1. every length on a pulse type's own grid plays as many steps as typed (Time2Tics);
  2. the amplitude table file (the second argument): the compiler's words equal the same arithmetic done here, a file
     that is not a table and a power above the file's top are refused with exit 2 and no RAW file, and without the
     argument the built-in conversion is used;
  3. --lab: every point of every <head>-manifest.json in a DDS day folder (e.g. Data/DDS Control/20261117) is compiled
     from the manifest's rows and compared with the -final.txt the lab's compiler wrote that day: byte for byte;
  4. --gui: Freq-Scan-GUI's model (ddsgui/ampword.py) gives the compiler's amplitude words for 400 random pulses, with
     the built-in conversion and with the table file.

x86_64, not arm64: the compiler computes tic counts and frequency words in long double, which is 80 bits on x86 (as in
the lab's MinGW build) and 64 on Apple silicon; an arm64 build differs from the lab's output in hundreds of words.
"""
import argparse, csv, glob, json, math, os, random, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), 'NewDDS2-Cooling2.0-Cal-V2')
EXAMPLE = os.path.join(os.path.dirname(HERE), 'amplitude_table.example.txt')


def amplitude_writes(lines):
    out, high = [], 0
    for line in lines:
        text = line.strip().strip('\x1a')
        if not text:
            continue
        value = int(text, 16)
        if value & 0xFF == 0x21:
            high = (value >> 8) & 0x0F
        elif value & 0xFF == 0x22:
            out.append((high << 8) | ((value >> 8) & 0xFF))
    return out


def bursts(words):
    out, cur = [], []
    for w in words:
        if w > 0:
            cur.append(w)
        elif cur:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lab'); ap.add_argument('--gui')
    args = ap.parse_args()
    work = tempfile.mkdtemp()
    exe = os.path.join(work, 'calv2')
    sources = sorted(glob.glob(os.path.join(SRC, '*.cpp')))
    subprocess.check_call(['clang++', '-arch', 'x86_64', '-I', os.path.join(HERE, 'stubs'), '-I', SRC, '-O2', '-w', '-o', exe] + sources)

    def run(rows, extra=()):
        with open(os.path.join(work, 'pt'), 'w', newline='') as f:
            f.write('Cool\n')
            csv.writer(f, dialect='excel-tab').writerows(rows)
        raw = os.path.join(work, 'RAWpt')
        r = subprocess.run([exe, 'pt'] + list(extra), cwd=work, capture_output=True, text=True)
        words = open(raw).read().split('\n')[:-1] if (r.returncode == 0 and os.path.exists(raw)) else None
        return r.returncode, r.stdout, words

    # 1. lengths on the grid
    bad = []
    for code, grid, ks in ((3, 1, list(range(1, 301)) + [500, 710, 1000, 5000, 50000]), (2, 2, range(1, 501)), (1, 8, range(1, 401))):
        for k in ks:
            rc, out, raw = run([[56.6e6, 0.0, k*grid/1000.0, 0.4, code, 'x']])
            got = None if raw is None else (len(raw) - 18 if code == 3 else len(amplitude_writes(raw)) - (2 if code == 2 else 0))
            if got != k:
                bad.append((code, k, got))
    assert not bad, bad[:10]
    print('1. lengths on the grid: 1205 compiled, all play as typed')

    # 2. the table file
    pts = []
    for line in open(EXAMPLE):
        t = line.split('#')[0].split()
        if len(t) == 2 and t[0] not in ('version', 'interpolation', 'rounding'):
            pts.append((float(t[0]), float(t[1])))
    U = [math.sqrt(p) for p, f in pts]; Y = [f for p, f in pts]

    def word(P):
        if not P > 0:
            return 0
        u = math.sqrt(P); jl, ju = 0, len(U) - 1
        if u >= U[ju]:
            return int(math.floor(4095.0*Y[ju] + 0.5))
        while ju - jl > 1:
            jm = (ju + jl) >> 1
            if u >= U[jm]:
                jl = jm
            else:
                ju = jm
        return int(math.floor(4095.0*(Y[jl] + (Y[ju] - Y[jl])*((u - U[jl])/(U[ju] - U[jl]))) + 0.5))
    random.seed(7)
    powers = [0.0, 1e-7, 0.0030546875, 0.01621810097, 0.4, 4.8, 5.18, 5.188000389] + [random.uniform(0, 5.188) for _ in range(150)] + [10**random.uniform(-6, -1.5) for _ in range(150)]
    rc, out, raw = run([[56.6e6, 0.0, 0.004, P, 3, 'sq'] for P in powers], [EXAMPLE])
    assert rc == 0 and 'Amplitude conversion: table file' in out, out[-300:]
    assert amplitude_writes(raw)[0::2] == [word(P) for P in powers]
    rc, out, raw = run([[56.6e6, 0.0, 0.004, 0.0030546875, 3, 'sq']])
    assert rc == 0 and 'built-in 2015 table' in out and amplitude_writes(raw)[0] == 40
    head = 'version 1\ninterpolation sqrt-linear\nrounding nearest\n'
    badfile = os.path.join(work, 'bad.txt')
    for text, needle in ((head + '0 0\n', 'fewer than 2'), ('rounding nearest\ninterpolation sqrt-linear\n0 0\n1 1\n', "'version 1' is missing"),
                         (head.replace('sqrt-linear', 'cubic') + '0 0\n1 1\n', 'not known'), (head + '0.001 0\n1 1\n', 'first point must be 0 0'),
                         (head + '0 0\n1 0.5\n0.5 0.7\n', 'must both rise'), (head + '0 0\n1 1.2\n', 'above 1'), (head + '0 0\n1 x\n', 'not a power')):
        open(badfile, 'w').write(text)
        rc, out, raw = run([[56.6e6, 0.0, 0.004, 0.1, 3, 'x']], [badfile])
        assert rc == 2 and raw is None and needle in out, (rc, out[-300:])
    open(badfile, 'w').write(head + '0 0\n1.0 0.5\n')
    rc, out, raw = run([[56.6e6, 0.0, 0.004, 2.0, 3, 'x']], [badfile])
    assert rc == 2 and raw is None and 'above the top of the power calibration table' in out
    rc, out, raw = run([[56.6e6, 0.0, 0.004, 0.1, 3, 'x']], [os.path.join(work, 'nofile.txt')])
    assert rc == 2 and raw is None and 'cannot open the file' in out
    print('2. amplitude table file: %d powers equal the arithmetic here; refusals exit 2 without a RAW file' % len(powers))

    # 3. the lab's compiled files
    if args.lab:
        total = exact = 0
        for mf in sorted(glob.glob(os.path.join(args.lab, '*-manifest.json')) + glob.glob(os.path.join(args.lab, 'playing', '*-manifest.json'))):
            m = json.load(open(mf))
            for pt in m['points']:
                final = open(os.path.join(os.path.dirname(mf), pt['file']), 'rb').read().rstrip(b'\x1a').decode().replace('\r\n', '\n').split('\n')
                if final[-1] == '':
                    final.pop()
                rc, out, raw = run(pt['rows'])
                total += 1
                exact += (raw is not None and final[-len(raw):] == raw)
        assert total and exact == total, (exact, total)
        print('3. the lab\'s compiled files in %s: %d points compiled from their manifest rows, all byte-identical' % (args.lab, total))

    # 4. the GUI's model
    if args.gui:
        sys.path.insert(0, args.gui)
        from ddsgui import ampword as aw
        random.seed(11)
        rows = []
        for i in range(400):
            code = random.choice((1, 2, 2, 3))
            L = {1: random.choice((3.0, 1.0, 0.504, 0.2)), 2: random.choice((0.12, 0.36, 0.96, 0.05, 0.034)), 3: random.choice((0.004, 0.05, 0.007))}[code]
            P = random.choice((random.uniform(0.0, 5.188), 10**random.uniform(-5, -1.3), random.uniform(0.01, 0.5)))
            rows.append([56.6e6, 0.0, L, P, code, 'p%d' % i])
        table = aw.load_table(EXAMPLE)
        for extra, tab in (([EXAMPLE], table), ([], None)):
            rc, out, raw = run(rows, extra)
            expected = []
            for r in rows:
                w = aw.pulse_words(r[4], r[2], r[3], tab)
                expected += bursts(w[:1] if r[4] == 3 else w)
            assert bursts(amplitude_writes(raw)) == expected
        print('4. Freq-Scan-GUI ddsgui/ampword.py: 400 random pulses, the compiler\'s amplitude words with the built-in conversion and with the table file')
    shutil.rmtree(work, ignore_errors=True)
    print('MAC CHECK OK')


if __name__ == '__main__':
    main()
