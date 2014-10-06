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

# NAME: read_pitch_tier
# OUT: PitchTier
# La funcion abre el archivo "12345.PitchTier", examina los
# campos xmin, xmax, y los atributos "number" y "value" de
# cada punto y los almacena en una clase llamada Pitchier
# que se encuentra declarada debajo de este comentario.

class PitchTier:
  def __init__(self):
    self.values = {}
    self.xmin = ""
    self.xmax = ""

def read_pitch_tier():
  text_file = open("12345.PitchTier", "r")
  lines = text_file.readlines()
  pitch = PitchTier()
  for line in lines:
    value = 0
    if "xmin" in line:
      l = line.split()
      pitch.xmin = float(l[-1])
    if "xmax" in line:
      l = line.split()
      pitch.xmax = float(l[-1])
    if "number" in line:
      l = line.split()
      number = float(l[-1])
    if "value" in line:
      l = line.split()
      value = float(l[-1])
      pitch.values[number] = value
  return pitch

# NAME: save_modified_pitch_tier
# IN: PitchTier
# OUT: "12345.PitchTier"
# La funcion crea un archivo PitchTier con los valores
# del Pitch pasado como parametro. 

def save_modified_pitch_tier(pitch):
  s = 'File type = "ooTextFile"\n' + \
      'Object class = "PitchTier"\n\n' + \
      'xmin = ' + str(pitch.xmin) + ' \n' + \
      'xmax = ' + str(pitch.xmax) + ' \n' + \
      'points: size = ' + str(len(pitch.values)) + ' \n'
  i = 0
  for key, value in sorted(pitch.values.items()):
    s = s + 'points [' + str(i+1) + ']:\n' + \
            '    number = ' + str(key) + ' \n' + \
            '    value = ' + str(value) + ' \n'
    i = i + 1 
  file = open("12345.PitchTier", "w")
  file.write(s)

# NAME: change_pitch_tier
# IN: PitchTier
# OUT: PitchTier
# La funcion modifica el PitchTier de entrada y lo retorna.

def value_mas_cercano(x, values):
  min = 999999
  for key in values:
    if abs(float(key)-float(x)) < min:
      min = abs(float(key)-float(x))
      min_key = key
  return float(values[min_key])

def delete_rango(rango, values):
  for key in values.keys():
    if float(key) >= rango[0] and float(key) <= rango[1]:
      del values[key]

def change_pitch_tier(pitch, difonos):
  di_prom = pitch.xmax/float(len(difonos))
  rangos = []
  rango = []
  x = 0
  for difono in difonos:      
    if "A" in difono:
      if len(rango) == 1:
        rango.append(x + di_prom)
        rangos.append(rango)
        rango = []
      elif len(rango) == 0:
        rango.append(x)
    x = x + di_prom
  for rango in rangos:
    a = 10
    b = value_mas_cercano(rango[0],pitch.values)
    c = 10
    largo_intervalos = (rango[1]-rango[0])/float(c)
    points = [rango[0] + i * largo_intervalos for i in range(0, c)]
    delete_rango(rango, pitch.values)
    for i in range(0,c):
      f = a * i + b
      pitch.values[points[i]] = f
  return pitch

# NAME: add_prosodia
# IN: wav file
# OUT: wav file
# La funcion toma un wav sin prosodia y se la agrega
# reemplazando el wav original.

def add_prosodia(output, difonos):
  os.system("./../praat extraer-pitch-track.praat " + output + " 12345.PitchTier 50 300")
  pitch_tier = read_pitch_tier()
  pitch_tier = change_pitch_tier(pitch_tier, difonos)
  save_modified_pitch_tier(pitch_tier)
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
    add_prosodia(output, difonos)
    os.system('rm 12345.PitchTier')

  os.system('rm ../difonos/script.praat')
