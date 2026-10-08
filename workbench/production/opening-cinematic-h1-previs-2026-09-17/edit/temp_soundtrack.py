"""Original procedural temp score / Foley for Joseon Hunters H1 previs.

This is an original, deterministic synthetic placeholder, NOT final Korean
traditional music and NOT a recording of traditional instruments. No external
recordings, compositions, voices, TTS, paid services, or sampled instruments are
used. Only NumPy mathematics and standard-library WAV/RIFF writing are used.
Both the score and Foley are authored for the current 50-second previs.

Rerun: python temp_soundtrack.py [--output path.wav]
Optional H09 sync override: --knocks 32.75 33.5
The score/Foley placements below are editable in seconds; no time stretching.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
import wave

import numpy as np

SR = 48000
DURATION = 50.0
SEED = 2026091701
TARGET_PEAK_DBFS = -3.0  # extra headroom below the requested -2 dBFS ceiling
RNG = np.random.default_rng(SEED)
N = round(SR * DURATION)
MIX = np.zeros((N, 2), dtype=np.float64)
EVENTS: list[dict] = []


def timebase(duration: float) -> np.ndarray:
    return np.arange(round(duration * SR), dtype=np.float64) / SR


def fade(signal: np.ndarray, attack: float = 0.015, release: float = 0.06) -> np.ndarray:
    signal = np.array(signal, dtype=np.float64, copy=True)
    a, r = min(len(signal), round(SR * attack)), min(len(signal), round(SR * release))
    if a:
        signal[:a] *= np.sin(np.linspace(0, math.pi / 2, a)) ** 2
    if r:
        signal[-r:] *= np.cos(np.linspace(0, math.pi / 2, r)) ** 2
    return signal


def noise(duration: float, low: float, high: float, tilt: float = 0.0) -> np.ndarray:
    n = round(SR * duration)
    raw = RNG.normal(0, 1, n)
    bins = np.fft.rfftfreq(n, 1 / SR)
    lo = 1 - np.exp(-((bins / max(low, 1)) ** 4))
    hi = np.exp(-((bins / high) ** 6))
    shape = lo * hi * (np.maximum(bins, low) / max(low, 1)) ** (-tilt)
    shape[0] = 0
    out = np.fft.irfft(np.fft.rfft(raw) * shape, n)
    return out / max(np.sqrt(np.mean(out * out)), 1e-12)


def add(signal: np.ndarray, at: float, amp: float, pan: float, name: str, echo=False):
    first = round(at * SR)
    if first < 0 or first >= N:
        raise ValueError((name, at))
    signal = np.asarray(signal, dtype=np.float64)
    left, right = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
    end = min(N, first + len(signal))
    stereo = signal[:end-first, None] * amp * np.array([left, right])
    MIX[first:end] += stereo
    if echo:
        for delay, gain in [(0.071, 0.075), (0.133, 0.045)]:
            start = first + round(delay * SR)
            stop = min(N, start + len(stereo))
            if stop > start:
                MIX[start:stop] += stereo[:stop-start, ::-1] * gain
    EVENTS.append({"name": name, "at": round(at, 4), "duration": round(len(signal)/SR, 4),
                   "amp": amp, "pan": pan})


def string_pad(duration: float, hz: float) -> np.ndarray:
    t = timebase(duration)
    vibrato = 0.0012 * np.sin(2 * math.pi * 0.43 * t)
    phase = 2 * math.pi * np.cumsum(hz * (1 + vibrato)) / SR
    out = sum(a * np.sin(k * phase + p) for k, a, p in
              [(1, .75, 0), (2, .22, .1), (3, .08, .2), (4, .025, .3)])
    # Extremely restrained bow texture; no horror beating or high dissonance.
    out += noise(duration, 120, 1700, .8) * .019
    out *= .9 + .1 * np.sin(2 * math.pi * .17 * t)
    return fade(out, min(2.0, duration / 4), min(2.4, duration / 3))


def pluck(duration: float, hz: float, brightness: float = 1.0) -> np.ndarray:
    t = timebase(duration)
    out = np.zeros_like(t)
    for k in range(1, 8):
        # Slightly inharmonic upper modes, with faster decay and soft attack.
        f = hz * k * (1 + .0008 * k * k)
        out += (1 / k**1.55) * np.sin(2 * math.pi * f * t) * np.exp(-t * (1.4 + .9*k))
    out += noise(duration, 550, 4800, .2) * np.exp(-t * 60) * .045 * brightness
    return fade(out, .008, .12)


def drum(duration: float, low: float = 64, woody: float = .16) -> np.ndarray:
    t = timebase(duration)
    pitch = low + 34 * np.exp(-t * 19)
    phase = 2 * math.pi * np.cumsum(pitch) / SR
    out = np.sin(phase) * np.exp(-t * 6.3)
    out += woody * np.sin(2 * math.pi * 177 * t) * np.exp(-t * 18)
    out += .047 * noise(duration, 110, 1100) * np.exp(-t * 26)
    return fade(out, .005, .11)


def wood_hit(duration: float, hz: float, dry: float = 1) -> np.ndarray:
    t = timebase(duration)
    out = sum(a * np.sin(2 * math.pi * hz * k * t) * np.exp(-t * d)
              for k, a, d in [(1, .75, 24), (1.61, .3, 33), (2.52, .13, 48)])
    out += .10 * dry * noise(duration, 420, 4200, .1) * np.exp(-t * 65)
    return fade(out, .0018, .035)


def cloth(duration: float, strength=1) -> np.ndarray:
    t = timebase(duration)
    env = np.sin(math.pi * np.minimum(t / duration, 1)) ** 1.7
    env *= .72 + .28 * np.sin(2 * math.pi * (5.1 * t + .8*t*t)) ** 2
    return fade(noise(duration, 450, 3500, .45) * env * strength, .03, .09)


def step(duration: float, weight: float) -> np.ndarray:
    t = timebase(duration)
    body = np.sin(2 * math.pi * (76 + weight * 7) * t) * np.exp(-t * 32) * .50
    gravel = noise(duration, 500, 4500, .5) * np.exp(-t * 25) * .19
    sole = noise(duration, 90, 700, .4) * np.exp(-t * 20) * .18
    return fade(body + gravel + sole, .004, .06)


def build(knocks: list[float]):
    # Continuous, very low exterior air with a quieter 21-27 second breathing space.
    t = timebase(DURATION)
    air = noise(DURATION, 65, 650, .65)
    env = np.interp(t, [0, 2, 17, 21, 27, 43, 46.5, 47, 49, 50],
                    [0, .011, .010, .007, .006, .008, .006, .005, .005, 0])
    add(fade(air * env, .15, 1.0), 0, 1, -.10, "exterior_air")
    add(fade(noise(DURATION, 110, 900, .8) * env * .24, .15, 1.0),
        0, 1, .45, "exterior_air_stereo")

    # Original score: matte low strings and sparse D pentatonic plucks, not final gugak.
    add(string_pad(17.0, 73.4162), 0, .040, -.25, "low_string_D2", True)
    add(string_pad(13.0, 110.0), 3, .018, .22, "low_string_A2", True)
    for at, hz, amp in [(4.3, 146.832, .019), (10.9, 110, .022), (14.0, 164.814, .017)]:
        add(pluck(2.0, hz), at, amp, .12, "sparse_opening_pluck", True)
    add(string_pad(5.0, 73.4162), 17, .041, .0, "reflection_low_string", True)
    # 21-27 stays mostly empty: sound events and breathing room carry the turn.
    add(pluck(1.7, 220), 24.1, .011, -.2, "transition_pluck", True)

    for i, at in enumerate(np.arange(27.0, 42.5, 4/3)):
        add(drum(.65, 62 if i % 2 == 0 else 69), float(at),
            .055 if i % 3 == 0 else .037, -.14, "doho_soft_low_drum", True)
        if i % 3 != 2:
            add(wood_hit(.19, 290 + 10 * (i % 3), .4), float(at + 2/3),
                .019, .23, "doho_quiet_wood_offbeat", True)
    for at, hz, pan, amp in [(27.4,146.832,-.15,.047),(30.05,220,.1,.045),
                             (34.1,164.814,-.1,.034),(37.3,146.832,.12,.038),
                             (39.35,110,-.18,.032),(42.0,146.832,.06,.040)]:
        add(pluck(2.0,hz),at,amp,pan,"doho_pentatonic_pluck",True)

    # H01: small stone contact and grain, not the same timbre as the later wood knocks.
    for at, hz, amp in [(1.18,820,.060),(1.46,1060,.039),(1.72,760,.027)]:
        tt=timebase(.25)
        sig=np.sin(2*math.pi*hz*tt)*np.exp(-tt*45)*.55
        sig+=noise(.25,850,6500,.2)*np.exp(-tt*24)*.18
        add(fade(sig,.0015,.04),at,amp,-.28,"H01_stone")
    add(cloth(.46),5.03,.040,.10,"H02_cloth")
    add(fade(noise(1.1,100,1200,.7)*np.sin(np.linspace(0,math.pi,round(1.1*SR)))**2,.07,.15),
        6.5,.023,-.3,"H02_wind")
    for at,dur,amp in [(9.5,.72,.024),(10.28,.65,.034)]:
        add(cloth(dur),at,amp,-.08,"H03_clothes")

    # H04 hinge/body resonance: softly varying friction plus a separate settling joint.
    tt=timebase(1.4)
    phase=2*math.pi*np.cumsum(155+18*np.sin(2*math.pi*1.1*tt))/SR
    creak=(np.sin(phase)*.16+np.sin(1.51*phase)*.065)
    # Retain the original RNG draw count so unrelated later score/Foley timbres
    # stay deterministic while this one friction event length changes.
    creak_texture=noise(1.2,160,1700,.4)
    creak+=np.interp(np.linspace(0,len(creak_texture)-1,len(tt)),
                     np.arange(len(creak_texture)),creak_texture)*.052
    creak*=np.sin(math.pi*tt/1.4)**1.5*(.6+.4*np.sin(2*math.pi*9.3*tt)**2)
    add(fade(creak,.06,.12),14.5,.22,.27,"H04_wood_creak")
    add(wood_hit(.23,225,.6),16.0,.048,.27,"H04_wood_settle",True)

    # H05 water: low splash bed + several short, different bubbly resonances.
    tt=timebase(1.4)
    ripple=noise(1.4,360,7200,.4)*np.exp(-tt*2.0)*(.3+.7*np.sin(math.pi*np.minimum(tt/.38,1))**2)
    add(fade(ripple,.015,.2),19.0,.033,-.1,"H05_water_ripple")
    for at,hz,amp in [(19.18,680,.009),(19.48,920,.009),(19.87,570,.007),(20.18,780,.006)]:
        tt=timebase(.24)
        phase=2*math.pi*(hz*tt + 260*tt*tt)
        add(fade(np.sin(phase)*np.exp(-tt*24),.005,.04),at,amp,.10,"H05_water_detail")
    add(cloth(.28)*.7 + wood_hit(.28,510,.15)*.15,26.05,.052,.18,"H07_fan")
    tt=timebase(1.65)
    bell=sum(a*np.sin(2*math.pi*f*tt)*np.exp(-tt*d) for f,a,d in
             [(910,1,3.1),(1451,.28,4.7),(2124,.10,7.5)])
    add(fade(bell,.006,.2),26.3,.022,-.24,"H07_small_bell",True)

    # H08 is trimmed from source 1-5s; observed plants 1.25/2.5 -> 27.25/28.5.
    # Corrected H10: source 1.75s - trim .5s + timeline 39s = 40.25s.
    # Still synthesize the retired fourth step without adding it, preserving
    # the seeded RNG stream and all later title/ambience timbres.
    for i,at in enumerate([27.25,28.5,40.25,None]):
        foot=step(.38,(i%2)*.7)
        if at is None:
            continue
        add(foot,at,.080 if at<30 else .070,
            -.1 if i%2==0 else .06,"H08_step" if at<30 else "H10_step")
    for i,at in enumerate(knocks):
        add(wood_hit(.30,355+13*i,.85),at,.112 if i==0 else .092,.28,
            "H09_knock_TIMING_ADJUSTABLE",True)

    # One restrained title accent; after 46.5 only very quiet exterior air remains.
    add(drum(1.7,48,.23),43.0,.25,.0,"title_low_hit",True)
    add(string_pad(3.5,73.4162),43.0,.023,.0,"title_short_low_tail",True)


def riff_chunk(tag: bytes, payload: bytes) -> bytes:
    return tag + struct.pack("<I",len(payload)) + payload + (b"\0" if len(payload)%2 else b"")


def write_wav(path: Path, pcm: np.ndarray, metadata: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as f:
        f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes(pcm.astype("<i2").tobytes())
    # Standard RIFF INFO keeps provenance in the one WAV; no extra owned sidecar.
    comment=("Original procedural temporary score and Foley. NOT final gugak. "
             "No external samples, recordings, compositions, voices, TTS, or paid services. "
             "All sound generated by this deterministic NumPy script; seed="+str(SEED)+". "+
             "H09 knock timing is provisional and adjustable. "+json.dumps(metadata,ensure_ascii=True))
    info=b"INFO"+riff_chunk(b"INAM",b"Joseon Hunters H1 original temp soundtrack\0")
    info+=riff_chunk(b"IART",b"Joseon Hunters project - procedural synthesis\0")
    info+=riff_chunk(b"ICMT",comment.encode("utf-8")+b"\0")
    with path.open("r+b") as f:
        f.seek(0,2);f.write(riff_chunk(b"LIST",info));size=f.tell();f.seek(4);f.write(struct.pack("<I",size-8))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output",type=Path,default=Path(__file__).with_name("temp_soundtrack.wav"))
    ap.add_argument("--knocks",nargs=2,type=float,default=[32.75,33.5])
    args=ap.parse_args()
    build(args.knocks)
    # Remove minute numerical DC; fade boundary and leave headroom, no hard limiter.
    MIX[:]-=MIX.mean(axis=0,keepdims=True)
    MIX[:round(.03*SR)]*=np.linspace(0,1,round(.03*SR))[:,None]
    MIX[-round(.75*SR):]*=np.linspace(1,0,round(.75*SR))[:,None]
    raw_peak=float(np.max(np.abs(MIX)))
    gain=10**(TARGET_PEAK_DBFS/20)/max(raw_peak,1e-12)
    MIX[:]*=gain
    # Low TPDF dither; final sample clipping is not used or needed.
    dither=(RNG.random(MIX.shape)-RNG.random(MIX.shape))/65536
    pcm=np.rint((MIX+dither)*32767).astype(np.int16)
    peak=float(np.max(np.abs(pcm.astype(np.float64))))/32768
    rms=float(np.sqrt(np.mean((pcm.astype(np.float64)/32768)**2)))
    metadata={"sample_rate":SR,"channels":2,"duration_seconds":DURATION,
              "sample_frames":N,"sample_peak_dbfs":round(20*math.log10(peak),4),
              "rms_dbfs":round(20*math.log10(rms),4),"master_gain":round(gain,6),
              "knock_seconds":args.knocks,"seed":SEED,"events":EVENTS}
    assert peak <= 10**(-2/20),peak
    assert not np.any(np.abs(pcm.astype(np.int32))>=32767)
    write_wav(args.output,pcm,metadata)
    blocks=[]
    for a,b in [(0,17),(17,21),(21,27),(27,43),(43,47),(47,50)]:
        block=pcm[round(a*SR):round(b*SR)].astype(np.float64)/32768
        blocks.append({"start":a,"end":b,"rms_dbfs":round(20*np.log10(np.sqrt(np.mean(block*block))),2)})
    print(json.dumps({"output":str(args.output.resolve()),"bytes":args.output.stat().st_size,
                      **{k:v for k,v in metadata.items() if k!='events'},
                      "section_levels":blocks,"event_count":len(EVENTS),
                      "sha256":hashlib.sha256(args.output.read_bytes()).hexdigest()},indent=2))


if __name__=="__main__":
    main()
