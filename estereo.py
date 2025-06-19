import struct as st

"""
Pau Dresaire

Este módulo contiene funciones para manipular señales en ficheros WAV:
- estereo2mono: convierte estéreo a mono (canal L, R, suma o diferencia)
- mono2estereo: crea estéreo a partir de dos señales mono
- codEstereo: codifica estéreo en 32 bits usando semisuma/semidiferencia
- decEstereo: reconstruye estéreo desde codificación 32b
"""

# -------------------------
# Funciones auxiliares WAV
# -------------------------

def desempaquetar_cabecera_wav(c):
    return dict(zip([
        "chunkId", "chunkSize", "format",
        "subchunk1Id", "subchunk1Size", "audioFormat",
        "numChannels", "sampleRate", "byteRate",
        "blockAlign", "bitsPerSample",
        "subchunk2Id", "subchunk2Size"
    ], st.unpack('<4sI4s4sIHHIIHH4sI', c)))

def empaquetar_cabecera_wav(c):
    return st.pack('<4sI4s4sIHHIIHH4sI',
        c["chunkId"], c["chunkSize"], c["format"],
        c["subchunk1Id"], c["subchunk1Size"], c["audioFormat"],
        c["numChannels"], c["sampleRate"], c["byteRate"],
        c["blockAlign"], c["bitsPerSample"],
        c["subchunk2Id"], c["subchunk2Size"]
    )

# -------------------------
# Estéreo a Mono
# -------------------------

def estereo2mono(ficEste, ficMono, canal=2):
    with open(ficEste, 'rb') as f:
        cab = desempaquetar_cabecera_wav(f.read(44))
        data = f.read()

    if cab["numChannels"] != 2 or cab["bitsPerSample"] != 16:
        print("El fichero debe ser estéreo de 16 bits.")
        return

    muestras = st.unpack('<' + 'h' * (len(data) // 2), data)
    L = muestras[::2]
    R = muestras[1::2]

    if canal == 0:
        mono = L
    elif canal == 1:
        mono = R
    elif canal == 2:
        mono = [(l + r) // 2 for l, r in zip(L, R)]
    elif canal == 3:
        mono = [(l - r) // 2 for l, r in zip(L, R)]
    else:
        raise ValueError("canal debe ser 0, 1, 2 o 3")

    datos = st.pack('<' + 'h' * len(mono), *mono)
    cab["numChannels"] = 1
    cab["blockAlign"] = cab["bitsPerSample"] // 8
    cab["byteRate"] = cab["sampleRate"] * cab["blockAlign"]
    cab["subchunk2Size"] = len(datos)
    cab["chunkSize"] = 36 + len(datos)

    with open(ficMono, 'wb') as f:
        f.write(empaquetar_cabecera_wav(cab))
        f.write(datos)

# -------------------------
# Mono a Estéreo
# -------------------------

def mono2estereo(ficIzq, ficDer, ficEste):
    with open(ficIzq, 'rb') as f1, open(ficDer, 'rb') as f2:
        cab1 = desempaquetar_cabecera_wav(f1.read(44))
        cab2 = desempaquetar_cabecera_wav(f2.read(44))
        data1 = f1.read()
        data2 = f2.read()

    if cab1["numChannels"] != 1 or cab2["numChannels"] != 1:
        print("Ambos archivos deben ser mono.")
        return
    if cab1["bitsPerSample"] != 16 or cab2["bitsPerSample"] != 16:
        print("Ambos deben tener muestras de 16 bits.")
        return

    m1 = st.unpack('<' + 'h' * (len(data1) // 2), data1)
    m2 = st.unpack('<' + 'h' * (len(data2) // 2), data2)

    intercalado = [val for pair in zip(m1, m2) for val in pair]
    datos = st.pack('<' + 'h' * len(intercalado), *intercalado)

    cab = cab1.copy()
    cab["numChannels"] = 2
    cab["blockAlign"] = cab["bitsPerSample"] // 8 * 2
    cab["byteRate"] = cab["sampleRate"] * cab["blockAlign"]
    cab["subchunk2Size"] = len(datos)
    cab["chunkSize"] = 36 + len(datos)

    with open(ficEste, 'wb') as f:
        f.write(empaquetar_cabecera_wav(cab))
        f.write(datos)

# -------------------------
# Codificación estéreo 32b
# -------------------------

def codEstereo(ficEste, ficCod):
    with open(ficEste, 'rb') as f:
        cab = desempaquetar_cabecera_wav(f.read(44))
        data = f.read()

    if cab["numChannels"] != 2 or cab["bitsPerSample"] != 16:
        print("Debe ser un WAV estéreo de 16 bits.")
        return

    muestras = st.unpack('<' + 'h' * (len(data) // 2), data)
    L = muestras[::2]
    R = muestras[1::2]

    codificadas = []
    for l, r in zip(L, R):
        s = (l + r) // 2
        d = (l - r) // 2
        word = ((s & 0xFFFF) << 16) | (d & 0xFFFF)
        codificadas.append(word)

    cab["numChannels"] = 1
    cab["bitsPerSample"] = 32
    cab["blockAlign"] = 4
    cab["byteRate"] = cab["sampleRate"] * 4
    cab["subchunk2Size"] = len(codificadas) * 4
    cab["chunkSize"] = 36 + cab["subchunk2Size"]

    with open(ficCod, 'wb') as f:
        f.write(empaquetar_cabecera_wav(cab))
        f.write(st.pack('<' + 'I' * len(codificadas), *codificadas))

# -------------------------
# Decodificación estéreo
# -------------------------

def decEstereo(ficCod, ficEste):
    with open(ficCod, 'rb') as f:
        cab = desempaquetar_cabecera_wav(f.read(44))
        data = f.read()

    if cab["numChannels"] != 1 or cab["bitsPerSample"] != 32:
        print("Debe ser WAV mono de 32 bits.")
        return

    muestras = st.unpack('<' + 'I' * (len(data) // 4), data)
    sL = []
    sR = []

    for x in muestras:
        s = st.unpack('<h', st.pack('<H', (x >> 16) & 0xFFFF))[0]
        d = st.unpack('<h', st.pack('<H', x & 0xFFFF))[0]
        l = max(-32768, min(32767, s + d))
        r = max(-32768, min(32767, s - d))
        sL.append(l)
        sR.append(r)

    intercalado = [val for pair in zip(sL, sR) for val in pair]
    datos = st.pack('<' + 'h' * len(intercalado), *intercalado)

    cab["numChannels"] = 2
    cab["bitsPerSample"] = 16
    cab["blockAlign"] = 4
    cab["byteRate"] = cab["sampleRate"] * 4
    cab["subchunk2Size"] = len(datos)
    cab["chunkSize"] = 36 + len(datos)

    with open(ficEste, 'wb') as f:
        f.write(empaquetar_cabecera_wav(cab))
        f.write(datos)

# -------------------------
# Pruebas (solo si se ejecuta directamente)
# -------------------------

if __name__ == "__main__":
    estereo2mono('wav/komm.wav', 'wav/salida_mono.wav')
    estereo2mono('wav/komm.wav', 'wav/salida_L.wav', canal=0)
    estereo2mono('wav/komm.wav', 'wav/salida_R.wav', canal=1)
    estereo2mono('wav/komm.wav', 'wav/salida_dif.wav', canal=3)

    mono2estereo('wav/salida_L.wav', 'wav/salida_R.wav', 'wav/reconstruido.wav')

    codEstereo('wav/komm.wav', 'wav/komm_codificado.wav')
    decEstereo('wav/komm_codificado.wav', 'wav/komm_decodificado.wav')
