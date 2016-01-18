import wave
import math
import struct

harm_max = 4.


def make_wav(data, transpose=0, pause=.05, repeat=0, fn="out.wav", silent=False):
    # wave settings
    f = wave.open(fn, 'w')

    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(44100)
    f.setcomptype('NONE', 'Not Compressed')

    bpm_fac = 120. / data['bpm']

    def length(l):
        return 88200. / l * bpm_fac

    def waves2(hz, l):
        a = 44100. / hz
        b = float(l) / 44100. * hz
        return [a, round(b)]

    def sixteen_bit(x):
        return struct.pack('h', round(32000 * x))

    def asin(x):
        return math.sin(2. * math.pi * x)

    def render2(a, b, vol):
        b2 = (1. - pause) * b
        l = waves2(a, b2)
        ow = ""
        q = int(l[0] * l[1])

        # harmonics are frequency-dependent:
        lf = math.log(a)
        lf_fac = (lf - 3.) / harm_max
        if lf_fac > 1:
            harm = 0
        else:
            harm = 2. * (1 - lf_fac)
        decay = 2. / lf
        t = (lf - 3.) / (8.5 - 3.)
        vol_fac = 1. + .8 * t * math.cos(math.pi / 5.3 * (lf - 3.))

        for x in range(q):
            fac = 1.
            if x < 100: fac = x / 80.
            if 100 <= x < 300: fac = 1.25 - (x - 100) / 800.
            if x > q - 400: fac = 1. - ((x - q + 400) / 400.)
            s = float(x) / float(q)
            dfac = 1. - s + s * decay
            ow += sixteen_bit((asin(float(x) / l[0])
                              + harm * asin(float(x) / (l[0] / 2.))
                              + .5 * harm * asin(float(x) / (l[0] / 4.))) / 4. * fac * vol * dfac * vol_fac)
        fill = max(int(ex_pos - curpos - q), 0)
        f.writeframesraw(ow + (sixteen_bit(0) * fill))
        return q + fill

    if not silent:
        print "Writing to file", fn
    curpos = 0
    ex_pos = 0.
    for rp in range(repeat + 1):
        for nn, x in enumerate(data['notes']):
            if nn % 10 == 0: print "[{0}/{1}]".format(nn+1, len(data["notes"]))
            if x[0] != '__' and int(x[3]) != 0 and int(x[4]) != 0:

                vol = 1.  # volume
                a = int(x[2])  # frequency
                a *= 2 ** transpose

                if int(x[4]) != 0 and int(x[3]) != 0:
                    if x[4] < 0:
                        b = length(-2. * (int(x[4]) / float(x[3])) / 3.)
                    else:
                        b = length(int(x[4]) / float(x[3]))

                ex_pos += b
                curpos += render2(a, b, vol)

            if x[0] == '__':
                b = length(int(x[4]) / float(x[3]))
                ex_pos += b
                f.writeframesraw(sixteen_bit(0) * int(b))
                curpos += int(b)

    f.writeframes('')
    f.close()
