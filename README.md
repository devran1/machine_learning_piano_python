# machine_learning_piano_python

for more explanation visit the link below

https://www.analyticsvidhya.com/blog/2020/01/how-to-perform-automatic-music-generation/

----------------------------------------------------------

it generate sounds for listening the sound install timidity

sudo apt install timidity

timidity  ...mid  <-- name of the song #makes you listen

to convert to mp3

timidity ......mid -Ow -o - | ffmpeg -i - -acodec libmp3lame -ab 64k output_file.mp3 #for exporting mid files to mp3
