#!/usr/bin/env python3

from music21 import *
import numpy as np

def read_it(file):

    #file="Bach_BWV888-02_008_20110315-SMD.mid"
    notes=[]
    notes_to_parse=None

    midi=converter.parse(file)

    s2=instrument.partitionByInstrument(midi)

    #print([j for i in s2 for j in i])

    for part in s2.parts:
        #print(str(part))
        #if "Piano" in str(part):
        notes_to_parse=part.recurse()

        for element in notes_to_parse:

            if isinstance(element,note.Note):
                notes.append(str(element.pitch))
            elif isinstance(element, chord.Chord):
                notes.append('.'.join(str(n) for n in element.normalOrder))    

    return np.array(notes)

#read_it()        
    #for i in part:
        #print(str(i))

import os

path="./midi_files/"
files=[i for i in os.listdir(path) if i.endswith(".mid")]
#print(files)
notes_array=np.array([read_it(path+i) for i in files], dtype=object)


notes_ = [element for note_ in  notes_array for element in note_]

#unique_notes=list(set(notes_))
#print(len(unique_notes))

from collections import Counter

freq=dict(Counter(notes_))

import matplotlib.pyplot as plt

no=[count for _, count in freq.items()]
#print(no)
#plt.figure(figsize=(5,5))

#plt.hist(no)
#plt.show()

frequent_notes=[note_ for note_ , count in freq.items() if count >=30]
#print(len(frequent_notes))



new_music=[]

for notes in notes_array:
    temp=[]
    for note_ in notes:
        if note_ in frequent_notes:
            temp.append(note_)
    new_music.append(temp)    
new_music=np.array(new_music, dtype=object)
#print(new_music)


no_of_timesteps=32
x=[]
y=[]

for note_ in new_music:
    for i in range(0,len(note_)-no_of_timesteps, 1):
        input_ = note_[i:i+no_of_timesteps]
        output = note_[i + no_of_timesteps]

        x.append(input_)
        y.append(output)

x=np.array(x)
y=np.array(y)

#print(y)

unique_x = list(set(x.ravel()))
x_note_to_int=dict((note_,number) for number, note_ in enumerate(unique_x))

x_seq=[]
for i in x:
    temp=[]
    for j in i:
        temp.append(x_note_to_int[j])
    x_seq.append(temp)
x_seq=np.array(x_seq)        

#print(x_seq)

unique_y =list(set(y))

y_note_to_int=dict((note_,number) for number, note_ in enumerate(unique_y))

y_seq=np.array([y_note_to_int[i] for i in y])

from sklearn.model_selection import train_test_split
x_tr, x_val, y_tr, y_val =train_test_split(x_seq,y_seq,test_size=0.2,random_state=0)

#print(x_tr,x_val,y_tr,y_val)

#import keras
#from keras import *

#def lstm():
#    model = Sequential()
#    model.add(LSTM(128,return_sequences=True))
#    model.add(LSTM(128))
#    model.add(Dense(256))
#    model.add(Activation('relu'))
#    model.add(Dense(n_vocab))
#    model.add(Activation('softmax'))
#    model.compile(loss='sparse_categorical_crossentropy',optimizer='adam')
#    return model



#lstm()
from keras.layers import *
from keras.models import *
from keras.callbacks import *
import keras.backend as K

K.clear_session()
model=Sequential()

model.add(Embedding(len(unique_x), 100, input_length=32,trainable=True))

model.add(Conv1D(64,3,padding='causal', activation='relu'))
model.add(Dropout(0.2))
model.add(MaxPool1D(2))

model.add(Conv1D(128,3,activation='relu',dilation_rate=2,padding='causal'))

#model.add(Conv1D(128,3,activation='relu',dilation_rate='2',padding='causal'))
model.add(Dropout(0.2))
model.add(MaxPool1D(2))

model.add(Conv1D(256,3,activation='relu',dilation_rate=4,padding='causal'))
model.add(Dropout(0.2))
model.add(MaxPool1D(2))

model.add(GlobalMaxPool1D())
model.add(Dense(256,activation='relu'))
model.add(Dense(len(unique_y), activation='softmax'))

model.compile(loss='sparse_categorical_crossentropy',optimizer='adam')

model.summary()

mc=ModelCheckpoint('best_model.h5',monitor="val_loss",mode="min",save_best_only=True,verbose=1)


#history=model.fit(np.array(x_tr),np.array(y_tr),batch_size=128,epochs=50,validation_data=(np.array(x_val),np.array(y_val)),verbose=1,callbacks=[mc])
history = model.fit(np.array(x_tr),np.array(y_tr),batch_size=128,epochs=50, validation_data=(np.array(x_val),np.array(y_val)),verbose=1, callbacks=[mc])



from keras.models import load_model


model=load_model('best_model.h5')


#works up to this point

import random
ind=np.random.randint(0,len(x_val)-1)

random_music=x_val[ind]

predictions=[]

for i in range(10):
    random_music=random_music.reshape(1,no_of_timesteps)
    prob=model.predict(random_music)[0]
    y_pred=np.argmax(prob,axis=0)
    predictions.append(y_pred)


    random_music=np.insert(random_music[0],len(random_music[0]),y_pred)
    random_music=random_music[1:]

#print(predictions)    

x_int_to_note=dict((number, note_) for number, note_ in enumerate(unique_x))
predicted_notes=[x_int_to_note[i] for i in predictions]



def convert_to_midi(prediction_output):
    offset=0
    output_notes=[]

    for pattern in prediction_output:

        if ('.' in pattern) or pattern.isdigit():
            notes_in_chord = pattern.split('.')
            notes=[]
            for current_note in notes_in_chord:
                cn=int(current_note)
                new_note=note.Note(cn)
                new_note.storedInstrument=instrument.Piano()
                notes.append(new_note)
            new_chord=chord.Chord(notes)
            new_chord.offset=offset

            output_notes.append(new_chord)

        else:
            new_note=note.Note(pattern)
            new_note.offset=offset 
            new_note.storedInstrument=instrument.Piano()
            output_notes.append(new_note)

        offset +=1
    midi_stream=stream.Stream(output_notes)
    midi_stream.write("midi",fp="music.mid")

convert_to_midi(predicted_notes)


























