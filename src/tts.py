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

# NAME: pitch_tier_to_array
# OUT: array
# La funcion abre el archivo "12345.PitchTier" y devuelve 
# un array con los valores de los campos "value" del archivo.

def pitch_tier_to_array():
  text_file = open("12345.PitchTier", "r")
  lines = text_file.readlines()
  values = []
  for line in lines:
    if "value" in line:
      l = line.split()
      values.append(l[-1])
  return values

# NAME: array_to_pitch_tier
# IN: array de values
# OUT: "12345.PitchTier"
# La funcion toma un array de values y reemplaza los campos
# "value" del archivo "12345.PitchTier" por los del array. 

def array_to_pitch_tier(array):
  text_file = open("12345.PitchTier", "r")
  lines = text_file.readlines()
  j = 0
  for i in range(0,len(lines)):
    if "value" in lines[i]:
      l = lines[i].split()
      l[-1] = array[j] + " \n"
      lines[i] = '    ' + ' '.join(l)
      j = j + 1
  s = ''.join(lines)
  file = open("12345.PitchTier", "w")
  file.write(s)

# NAME: add_prosodia
# IN: wav file
# OUT: wav file
# La funcion toma un wav sin prosodia y se la agrega
# reemplazando el wav original.

def add_prosodia(output):
  os.system("./../praat extraer-pitch-track.praat " + output + " 12345.PitchTier 50 300")
  values = pitch_tier_to_array()

## Modificamos los values ##

  values = [str(160) for value in values]

############################

  array_to_pitch_tier(values)
  os.system("./../praat reemplazar-pitch-track.praat " + output + " 12345.PitchTier " + output + " 50 300")

if __name__ == '__main__':

  texto = sys.argv[1]

# El output deberia ser pasado como parametro.

  output = "../palabras/" + texto + ".wav"

# Obtenemos los difonos del texto.

  difonos = split(texto)

# Verificamos si el texto es una pregunta o no.

  pregunta = 0
  if difonos[-1] == "?":
    pregunta = 1
    difonos.pop()

  gen_script(difonos, output)

# Combinamos los difonos del texto.

  os.system('./../praat ../difonos/script.praat')

# Agregamos la prosodia en caso de ser necesario.

  if pregunta:
    add_prosodia(output)

  os.system('rm ../difonos/script.praat')
  os.system('rm 12345.PitchTier')