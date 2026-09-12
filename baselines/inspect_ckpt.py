# Static, NON-EXECUTING inspection of a PyTorch checkpoint.
# Reads the zip container and walks the pickle opcodes with pickletools.
# Never calls pickle.load / torch.load, so no third-party code runs.
import sys, zipfile, pickletools, io, collections
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

path = sys.argv[1]
zf = zipfile.ZipFile(path)
names = zf.namelist()
pkls = [n for n in names if n.endswith('data.pkl')]
print('zip entries:', len(names), '| pickle:', pkls)
raw = zf.read(pkls[0])

globals_used = collections.Counter()
ops = list(pickletools.genops(io.BytesIO(raw)))
for i, (op, arg, pos) in enumerate(ops):
    if op.name in ('STACK_GLOBAL',):
        # the two preceding SHORT_BINUNICODE args are module, name
        prev = [a for (o, a, p) in ops[max(0, i - 4):i] if isinstance(a, str)]
        if len(prev) >= 2:
            globals_used[prev[-2] + '.' + prev[-1]] += 1
    elif op.name in ('GLOBAL',):
        globals_used[str(arg).replace(' ', '.')] += 1

print('\n--- classes/functions the pickle will import on load ---')
for k, v in globals_used.most_common():
    print('  %4d  %s' % (v, k))

# tensor storages -> parameter count
sizes = [zf.getinfo(n).file_size for n in names if '/data/' in n]
print('\nstorage records: %d, total bytes: %d (~%d fp32 params)'
      % (len(sizes), sum(sizes), sum(sizes) // 4))
