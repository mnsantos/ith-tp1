import sys
import os

# NAME: split
# IN: string
# OUT: array de los difonos que componen el string de entrada. Si el string presenta
# un signo de interrogacion se inserta como ultimo elemento del array.

def split(string):
  pregunta = 0
  if string[-1] == "?":
    pregunta = 1
    string = string[:len(string)-1]
  s = "x"
  for i in range(0,len(string)):
    s = s + string[i]*2
  s = s + "x"
  array = [s[i:i+2] for i in range(0, len(s), 2)]
  if pregunta:
    array.append("?") 
  return array

# NAME: gen_script
# IN: array de difonos, output
# OUT: praat script en ../difonos/script.praat
# La funcion toma un array de difonos a combinar y crea un script
# en Praat que los combina y guarda el wav resultante
# en el output tomado como parametro.

def gen_script(array, output):
  text_file = open("../difonos/script.praat", "w")
  s = ""
  i = 1
  for difono in array:
    s = s + 'Read from file: "' + difono + '.wav"\n'
    s = s + 'Rename: "' + str(i) + '"\n'
    i = i + 1
  s = s + '\n'
  for i in range(1,len(array)+1):
    if i == 1:
      s = s + 'selectObject: "Sound ' + str(i) + '"\n'
    else:
      s = s + 'plusObject: "Sound ' + str(i) + '"\n'
  s = s + "Concatenate recoverably\n\n" + \
          'selectObject: "Sound chain"\n' + \
          'Save as WAV file: "'
  if output[0] == "/":
    s = s + output + '"'
  else:
    s = s + '../src/' + output + '"'
  text_file.write(s)

if __name__ == '__main__':

  texto = sys.argv[1]
# El output deberia ser pasado como parametro.
  output = "../palabras/" + texto + ".wav"

  difonos = split(texto)

  gen_script(difonos, output)
  os.system('./../praat ../difonos/script.praat')

  os.system('rm ../difonos/script.praat')