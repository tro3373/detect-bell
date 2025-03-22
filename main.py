import pyaudio
import wave
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def show_devices():
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        print((i, dev["name"], dev["maxInputChannels"]))


def record_bell():
    input_device_index = 2  # 先ほど確認したデバイス番号

    chunk = 1024
    format = pyaudio.paInt16
    channels = 1  # モノラル入力 # 先ほど確認したmaxInputChannelsが上限
    rate = 44100
    record_seconds = 5

    p = pyaudio.PyAudio()
    stream = p.open(
        format=format,
        channels=channels,
        input_device_index=input_device_index,
        rate=rate,
        input=True,
        frames_per_buffer=chunk,
    )

    print("Recording...")
    frames = []
    for i in range(0, int(rate / chunk * record_seconds)):
        data = stream.read(chunk, exception_on_overflow=False)
        frames.append(data)
    print("Done!")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open("output.wav", "wb")
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b"".join(frames))
    wf.close()


def show_plot():
    file_name = "output.wav"  # 録音ファイル
    RATE = 44100  # 録音時に設定したRATE

    wf = wave.open(file_name, "rb")
    data = np.frombuffer(wf.readframes(wf.getnframes()), dtype="int16")
    wf.close()

    x = np.arange(data.shape[0]) / RATE
    plt.plot(x, data)
    plt.show()  # 横軸:時間(sec)
    x = [i for i in range(len(data))]
    plt.plot(x, data)
    plt.show()  # 横軸:データ点インデックス


def fft():
    file_name = "output.wav"  # 録音ファイル
    RATE = 44100  # 録音時に設定したRATE

    wf = wave.open(file_name, "rb")
    data = np.frombuffer(wf.readframes(wf.getnframes()), dtype="int16")
    wf.close()

    fft_data = np.abs(np.fft.fft(data))  # FFTした信号の強度
    freqList = np.fft.fftfreq(
        data.shape[0], d=1.0 / RATE
    )  # 周波数（グラフの横軸）の取得
    plt.plot(freqList, fft_data)
    plt.xlim(0, 5000)  # 0～5000Hzまでとりあえず表示する
    plt.show()


def fft_partial():
    file_name = "output.wav"  # 録音ファイル
    RATE = 44100  # 録音時に設定したRATE
    CHUNK = 1024 * 8  # 録音時に設定したCHUNK
    RECORD_SECONDS = 1  # 検出に使いたい秒数
    pnts = int(RATE / CHUNK * RECORD_SECONDS) * CHUNK  # dataが何点になるかを計算

    start = 0  # ここをいろいろ変えてみる

    wf = wave.open(file_name, "rb")
    data = np.frombuffer(wf.readframes(wf.getnframes()), dtype="int16")
    wf.close()

    data = data[start : start + pnts]
    fft_data = np.abs(np.fft.fft(data))  # FFTした信号の強度
    freqList = np.fft.fftfreq(
        data.shape[0], d=1.0 / RATE
    )  # 周波数（グラフの横軸）の取得
    plt.plot(freqList, fft_data)
    plt.xlim(0, 5000)  # 0～5000Hzまでとりあえず表示する
    plt.show()


def print_indices():
    file_name = "output.wav"  # 録音ファイル
    RATE = 44100  # 録音時に設定したRATE
    CHUNK = 1024 * 8  # 録音時に設定したCHUNK
    RECORD_SECONDS = 1  # 検出に使いたい秒数
    pnts = int(RATE / CHUNK * RECORD_SECONDS) * CHUNK  # dataが何点になるかを計算

    start = 0  # ここをいろいろ変えてみる

    wf = wave.open(file_name, "rb")
    data = np.frombuffer(wf.readframes(wf.getnframes()), dtype="int16")
    wf.close()

    data = data[start : start + pnts]
    fft_data = np.abs(np.fft.fft(data))
    freqList = np.fft.fftfreq(data.shape[0], d=1.0 / RATE)

    df = pd.DataFrame(dict(freq=freqList, amp=fft_data))
    df = df[df["freq"] > 500]  # 500 Hz以下は無視する。
    df = df[df["amp"] > 0.5e7]  # 0.5e7以上の強度を持つ点を覚える。
    print(list(df.index))
    # [610, 611, 612, 613, 615, 616, 1831, 1832, 1833, 1834, 1835, 1836, 3056, 3057, 3058, 3059, 4277, 4278, 4280, 4281, 4282, 4283, 4285]
    print(list(df["freq"]))
    # [656.7626953125, 657.83935546875, 658.916015625, 659.99267578125, 662.14599609375, 663.22265625, 1971.36474609375, 1972.44140625, 1973.51806640625, 1974.5947265625, 1975.67138671875, 1976.748046875, 3290.2734375, 3291.35009765625, 3292.4267578125, 3293.50341796875, 4604.87548828125, 4605.9521484375, 4608.10546875, 4609.18212890625, 4610.2587890625, 4611.33544921875, 4613.48876953125]
    print(len(df))
    # 23


def print_amp():
    file_name = "output.wav"  # 録音ファイル
    RATE = 44100  # 録音時に設定したRATE
    CHUNK = 1024 * 8  # 録音時に設定したCHUNK
    RECORD_SECONDS = 1  # 検出に使いたい秒数
    pnts = int(RATE / CHUNK * RECORD_SECONDS) * CHUNK  # dataが何点になるかを計算

    # ここに先ほどの結果を入れる
    freq_indices = [
        610,
        611,
        612,
        613,
        615,
        616,
        1831,
        1832,
        1833,
        1834,
        1835,
        1836,
        3056,
        3057,
        3058,
        3059,
        4277,
        4278,
        4280,
        4281,
        4282,
        4283,
        4285,
    ]

    start = 0  # ここをいろいろ変えてみる

    wf = wave.open(file_name, "rb")
    data = np.frombuffer(wf.readframes(wf.getnframes()), dtype="int16")
    wf.close()

    data = data[start : start + pnts]
    fft_data = np.abs(np.fft.fft(data))  # FFTした信号の強度

    amp = 0
    for i in freq_indices:
        amp += fft_data[i]

    print("{:.2e}".format(amp))
    # 3.24e+08


def main():
    show_devices()
    record_bell()


if __name__ == "__main__":
    main()
