import numpy as np, wave, json
SR=None; segs=[]
for i in range(1,9):
    w=wave.open(f'narr/n{i}.wav'); SR=w.getframerate(); ch=w.getnchannels()
    a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)
    if ch>1: a=a.reshape(-1,ch).mean(1)
    idx=np.where(np.abs(a)>600)[0]; a=a[max(0,idx[0]-200):idx[-1]+400]; segs.append(a)
out=[];scenes=[];speech=[];t=0
for k,a in enumerate(segs):
    pre=0.3; post=0.5 if k<7 else 1.2
    d=len(a)/SR; scenes.append([round(t,3),round(pre+d+post,3)]); speech.append([round(t+pre,3),round(t+pre+d,3)])
    out+= [np.zeros(int(pre*SR)),a,np.zeros(int(post*SR))]; t+=pre+d+post
v=np.concatenate(out).clip(-32768,32767).astype(np.int16)
w=wave.open('voice.wav','wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes(v.tobytes());w.close()
json.dump({'scenes':scenes,'speech':speech,'total':round(len(v)/SR,3)},open('timing.json','w'))
print(scenes,round(len(v)/SR,2))
